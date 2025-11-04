"""
Módulo de agentes de IA con funciones/tools
Contiene el agente de onboarding y el agente de diálogo
"""
import os
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Cargar variables de entorno antes de importar database
load_dotenv()

from database import database

logger = logging.getLogger(__name__)

class Agent:
    """Clase base para agentes de IA"""
    
    def __init__(self, system_prompt: str, model: str = None):
        self.system_prompt = system_prompt
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Inicializa el cliente de OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            # Verificar que la key no esté vacía
            if not api_key.strip():
                logger.warning("OPENAI_API_KEY está vacía")
                self.client = None
                return
            try:
                self.client = AsyncOpenAI(api_key=api_key)
                logger.info(f"Cliente OpenAI inicializado para agente (modelo: {self.model})")
                logger.debug(f"API Key configurada (primeros 10 chars): {api_key[:10]}...")
            except Exception as e:
                logger.error(f"Error inicializando cliente OpenAI: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                self.client = None
        else:
            logger.warning("OPENAI_API_KEY no encontrada en variables de entorno")
    
    def _ensure_client(self):
        """Asegura que el cliente esté inicializado, reintenta si es necesario"""
        if not self.client:
            logger.warning("Cliente no inicializado, reintentando...")
            self._init_client()
        return self.client is not None
    
    async def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una función del agente"""
        raise NotImplementedError("Subclases deben implementar _call_function")
    
    async def process_message(
        self, 
        user_message: str, 
        phone_number: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Procesa un mensaje del usuario y genera una respuesta
        
        Args:
            user_message: Mensaje del usuario
            phone_number: Número de teléfono del usuario
            conversation_history: Historial de conversación
            
        Returns:
            Respuesta del agente
        """
        # Asegurar que el cliente esté inicializado
        if not self._ensure_client():
            logger.error("Cliente OpenAI no inicializado después de reintento")
            return "Lo siento, el servicio de IA no está configurado."
        
        if not user_message or not user_message.strip():
            return "Por favor, envía un mensaje válido."
        
        if conversation_history is None:
            conversation_history = []
        
        # Construir mensajes
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Agregar historial
        for msg in conversation_history[-10:]:  # Últimos 10 mensajes
            messages.append(msg)
        
        # Agregar mensaje actual
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Llamar a OpenAI con función calling
        try:
            tools = self.get_tools()
            logger.debug(f"Llamando a OpenAI con modelo {self.model}, {len(tools)} herramientas disponibles")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                max_tokens=1000,
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            # Si el modelo quiere llamar una función
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parseando argumentos de función {function_name}: {e}")
                    logger.error(f"Argumentos recibidos: {tool_call.function.arguments}")
                    return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."
                
                # Ejecutar función
                try:
                    function_result = await self._call_function(function_name, function_args)
                except Exception as e:
                    logger.error(f"Error ejecutando función {function_name}: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    function_result = {
                        "success": False,
                        "error": f"Error ejecutando función: {str(e)}"
                    }
                
                # Agregar respuesta de función al contexto
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
                
                # Obtener respuesta final del modelo
                try:
                    final_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    return final_response.choices[0].message.content
                except Exception as e:
                    logger.error(f"Error en segunda llamada a OpenAI después de función: {str(e)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Si falla la segunda llamada, al menos devolver el resultado de la función
                    error_str = str(e)
                    if "401" in error_str or "Unauthorized" in error_str or "invalid_api_key" in error_str:
                        logger.error("⚠️  API Key rechazada en segunda llamada")
                        return "Lo siento, hay un problema con la configuración del servicio de IA. Por favor contacta al administrador."
                    raise
            else:
                return message.content
                
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            import traceback
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            
            # Detectar errores específicos de autenticación
            error_str = str(e)
            if "401" in error_str or "Unauthorized" in error_str or "invalid_api_key" in error_str:
                logger.error("⚠️  API Key de OpenAI inválida o expirada")
                return "Lo siento, hay un problema con la configuración del servicio de IA. Por favor contacta al administrador."
            elif "429" in error_str or "rate_limit" in error_str:
                return "Lo siento, he alcanzado el límite de solicitudes. Por favor intenta de nuevo en unos momentos."
            
            return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna las herramientas disponibles para el agente"""
        raise NotImplementedError("Subclases deben implementar get_tools")


class OnboardingAgent(Agent):
    """Agente de onboarding para registrar nuevos usuarios"""
    
    def __init__(self):
        system_prompt = """Eres un asistente amigable y entusiasta especializado en onboarding de nuevos usuarios.

Tu misión es ayudar a los usuarios a registrarse en el sistema de retos diarios. Debes:
1. Dar la bienvenida de manera cálida y personalizada
2. Pedir el nombre del usuario de forma natural
3. Entender sus intereses mediante una conversación fluida (no solo preguntar directamente)
4. Una vez que tengas nombre e intereses claros, usar la función register_user para registrarlos
5. Ser paciente y conversacional, no hacer sentir al usuario como si llenara un formulario

IMPORTANTE: Solo debes llamar a register_user cuando tengas tanto el nombre como los intereses del usuario claramente identificados. Si falta alguno, continúa la conversación de forma natural hasta obtenerlo."""
        
        super().__init__(system_prompt)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Herramientas disponibles para el agente de onboarding"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "register_user",
                    "description": "Registra un nuevo usuario en el sistema con su nombre y párrafo de intereses. Solo debes llamar esta función cuando tengas tanto el nombre como los intereses del usuario claramente identificados.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "El nombre completo o cómo quiere ser llamado el usuario"
                            },
                            "interests": {
                                "type": "string",
                                "description": "Un párrafo descriptivo sobre los intereses, hobbies, pasiones o temas que le interesan al usuario. Debe ser un texto completo y descriptivo, no solo palabras sueltas."
                            }
                        },
                        "required": ["name", "interests"]
                    }
                }
            }
        ]
    
    async def process_message(
        self, 
        user_message: str, 
        phone_number: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Procesa mensaje con el agente de onboarding, inyectando phone_number en las funciones"""
        # Guardar phone_number para usarlo en las funciones
        self._current_phone_number = phone_number
        return await super().process_message(user_message, phone_number, conversation_history)
    
    async def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta las funciones del agente de onboarding"""
        if function_name == "register_user":
            # Usar el phone_number guardado
            phone_number = getattr(self, '_current_phone_number', None)
            if not phone_number:
                return {
                    "success": False,
                    "error": "phone_number no disponible"
                }
            
            name = arguments.get("name")
            interests = arguments.get("interests")
            
            if not name or not interests:
                return {
                    "success": False,
                    "error": "name e interests son requeridos"
                }
            
            success = await database.create_user(phone_number, name, interests)
            
            if success:
                return {
                    "success": True,
                    "message": f"Usuario {name} registrado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudo registrar el usuario en la base de datos"
                }
        
        return {"success": False, "error": f"Función desconocida: {function_name}"}


class DialogueAgent(Agent):
    """Agente de diálogo para usuarios registrados - genera retos diarios y actualiza intereses"""
    
    def __init__(self):
        system_prompt = """Eres un asistente motivador y creativo especializado en generar retos diarios personalizados.

Tu misión es:
1. Mantener conversaciones naturales y amigables con usuarios ya registrados
2. Generar retos diarios creativos y personalizados basados en los intereses del usuario
3. Motivarlos a completar los retos
4. Celebrar sus logros
5. Actualizar sus intereses cuando el usuario lo mencione o cuando sea relevante

IMPORTANTE:
- Cada día debes proponer un reto nuevo y diferente
- Los retos deben ser desafiantes pero alcanzables
- Los retos deben estar relacionados con los intereses del usuario
- Si el usuario menciona nuevos intereses o cambios en sus gustos, usa update_interests para actualizarlos
- Sé creativo y variado en los retos (pueden ser de aprendizaje, creatividad, ejercicio, socialización, etc.)
- Si el usuario completa un reto, celébralo y propón el siguiente"""
        
        super().__init__(system_prompt)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Herramientas disponibles para el agente de diálogo"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "update_interests",
                    "description": "Actualiza los intereses del usuario cuando menciona nuevos intereses, cambios en sus gustos, o cuando descubres información relevante sobre lo que le interesa.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "interests": {
                                "type": "string",
                                "description": "El nuevo párrafo completo que describe los intereses actualizados del usuario"
                            }
                        },
                        "required": ["interests"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_info",
                    "description": "Obtiene la información del usuario (nombre, intereses, retos completados) para personalizar mejor los retos y conversaciones.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mark_challenge_completed",
                    "description": "Marca un reto como completado cuando el usuario indica que lo ha terminado o logrado.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    async def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta las funciones del agente de diálogo"""
        phone_number = getattr(self, '_current_phone_number', None)
        
        if function_name == "update_interests":
            if not phone_number:
                return {"success": False, "error": "phone_number no disponible"}
            
            interests = arguments.get("interests")
            if not interests:
                return {"success": False, "error": "interests es requerido"}
            
            success = await database.update_user_interests(phone_number, interests)
            
            if success:
                return {
                    "success": True,
                    "message": "Intereses actualizados correctamente"
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudieron actualizar los intereses"
                }
        
        elif function_name == "get_user_info":
            if not phone_number:
                return {"success": False, "error": "phone_number no disponible"}
            
            user = await database.get_user(phone_number)
            if user:
                return {
                    "success": True,
                    "user": {
                        "name": user.get("name"),
                        "interests": user.get("interests"),
                        "challenges_completed": user.get("challenges_completed", 0),
                        "last_challenge_date": user.get("last_challenge_date")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Usuario no encontrado"
                }
        
        elif function_name == "mark_challenge_completed":
            if not phone_number:
                return {"success": False, "error": "phone_number no disponible"}
            
            success = await database.increment_challenges_completed(phone_number)
            
            if success:
                return {
                    "success": True,
                    "message": "Reto marcado como completado"
                }
            else:
                return {
                    "success": False,
                    "error": "No se pudo marcar el reto como completado"
                }
        
        return {"success": False, "error": f"Función desconocida: {function_name}"}
    
    async def process_message(
        self, 
        user_message: str, 
        phone_number: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Procesa mensaje con el agente de diálogo, cargando información del usuario primero"""
        # Guardar phone_number para las funciones
        self._current_phone_number = phone_number
        
        # Obtener información del usuario para contexto
        user = await database.get_user(phone_number)
        if user:
            # Agregar contexto del usuario al system prompt
            user_context = f"\n\nInformación del usuario:\n- Nombre: {user.get('name')}\n- Intereses: {user.get('interests')}\n- Retos completados: {user.get('challenges_completed', 0)}\n"
            
            # Construir mensajes con contexto
            if conversation_history is None:
                conversation_history = []
            
            messages = [
                {"role": "system", "content": self.system_prompt + user_context}
            ]
            
            # Agregar historial
            for msg in conversation_history[-10:]:
                messages.append(msg)
            
            # Agregar mensaje actual
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Llamar a OpenAI
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.get_tools(),
                    tool_choice="auto",
                    max_tokens=1000,
                    temperature=0.7
                )
                
                message = response.choices[0].message
                
                # Si hay tool calls
                if message.tool_calls:
                    tool_call = message.tool_calls[0]
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Ejecutar función
                    function_result = await self._call_function(function_name, function_args)
                    
                    # Agregar respuesta de función
                    messages.append(message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(function_result)
                    })
                    
                    # Respuesta final
                    final_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    
                    return final_response.choices[0].message.content
                else:
                    return message.content
                    
            except Exception as e:
                logger.error(f"Error procesando mensaje: {str(e)}")
                return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."
        else:
            return "Parece que no estás registrado. Por favor, contacta al servicio de onboarding."

# Instancias globales
logger.info("Inicializando agentes...")
logger.debug(f"OPENAI_API_KEY disponible al inicializar: {bool(os.getenv('OPENAI_API_KEY'))}")
onboarding_agent = OnboardingAgent()
dialogue_agent = DialogueAgent()
logger.info(f"Agentes inicializados - Onboarding cliente: {onboarding_agent.client is not None}, Diálogo cliente: {dialogue_agent.client is not None}")

