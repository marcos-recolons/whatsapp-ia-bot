"""
Módulo de agentes de IA con funciones/tools
Contiene el agente de onboarding y el agente de diálogo
"""
import os
import logging
import json
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Google GenAI imports
try:
    from google import genai
    from google.genai import types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from google.api_core.datetime_helpers import DatetimeWithNanoseconds
    # Esto es legacy de firebase/google-cloud, puede no ser necesario con google-genai
except ImportError:  # pragma: no cover
    DatetimeWithNanoseconds = None

# Cargar variables de entorno antes de importar database
load_dotenv()

from database import database

logger = logging.getLogger(__name__)

_PROMPTS_CACHE: Optional[Dict[str, str]] = None
_PROMPTS_PATH = Path(os.getenv("SYSTEM_PROMPTS_FILE", Path(__file__).resolve().parent / "system_prompts.json"))


def _load_prompts() -> Dict[str, str]:
    global _PROMPTS_CACHE
    if _PROMPTS_CACHE is not None:
        return _PROMPTS_CACHE

    try:
        if not _PROMPTS_PATH.exists():
            logger.warning("Archivo de system prompts no encontrado en %s", _PROMPTS_PATH)
            _PROMPTS_CACHE = {}
        else:
            with _PROMPTS_PATH.open("r", encoding="utf-8") as prompts_file:
                _PROMPTS_CACHE = json.load(prompts_file)
    except Exception as exc:
        logger.error("Error cargando system prompts: %s", exc)
        _PROMPTS_CACHE = {}

    return _PROMPTS_CACHE


def get_system_prompt(prompt_key: str, fallback: str) -> str:
    prompts = _load_prompts()
    prompt_value = prompts.get(prompt_key)
    if prompt_value:
        return prompt_value
    logger.warning("System prompt '%s' no encontrado en JSON, usando fallback", prompt_key)
    return fallback


class Agent:
    """Clase base para agentes de IA"""
    
    def __init__(self, system_prompt: str, model: str = None):
        self.system_prompt = system_prompt
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        
        # Configurar modelo según proveedor
        if self.provider == "gemini":
            self.model = model or os.getenv("GEMINI_MODEL", "gemini-3-pro-preview")
        else:
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
            
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Inicializa el cliente según el proveedor configurado"""
        if self.provider == "gemini":
            self._init_gemini_client()
        else:
            self._init_openai_client()

    def _init_openai_client(self):
        """Inicializa el cliente de OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            if not api_key.strip():
                logger.warning("OPENAI_API_KEY está vacía")
                self.client = None
                return
            try:
                self.client = AsyncOpenAI(api_key=api_key)
                logger.info(f"Cliente OpenAI inicializado (modelo: {self.model})")
            except Exception as e:
                logger.error(f"Error inicializando OpenAI: {str(e)}")
                self.client = None
        else:
            logger.warning("OPENAI_API_KEY no encontrada")

    def _init_gemini_client(self):
        """Inicializa el cliente de Gemini"""
        if not HAS_GEMINI:
            logger.error("Librería google-genai no instalada. Ejecuta pip install google-genai")
            self.client = None
            return

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            if not api_key.strip():
                logger.warning("GEMINI_API_KEY está vacía")
                self.client = None
                return
            try:
                # Inicializar cliente Gemini
                # Nota: Para uso asíncrono, usaremos client.aio...
                self.client = genai.Client(api_key=api_key)
                logger.info(f"Cliente Gemini inicializado (modelo: {self.model})")
            except Exception as e:
                logger.error(f"Error inicializando Gemini: {str(e)}")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY no encontrada")
    
    def _ensure_client(self):
        """Asegura que el cliente esté inicializado"""
        if not self.client:
            logger.warning("Cliente no inicializado, reintentando...")
            self._init_client()
        return self.client is not None

    def _json_default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if DatetimeWithNanoseconds and isinstance(obj, DatetimeWithNanoseconds):
            return obj.isoformat()
        return str(obj)

    async def _create_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        context: str = "default"
    ):
        """Crea una completion usando OpenAI"""
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice

        def _kwargs_to_log(kwargs: Dict[str, Any]) -> Dict[str, Any]:
            return {k: v for k, v in kwargs.items() if k not in {"messages", "tools"}}

        try:
            logger.debug("Enviando completion OpenAI (%s)", context)
            return await self.client.chat.completions.create(**kwargs)
        except Exception as e:
            logger.error(f"Error en completion OpenAI ({context}): {str(e)}")
            raise

    async def _create_gemini_completion(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        context: str = "default"
    ):
        """Crea una completion usando Gemini"""
        try:
            logger.debug("Enviando completion Gemini (%s)", context)
            
            # 1. Convertir mensajes
            gemini_contents = []
            system_instruction = None
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    # Gemini 2.0/3.0 soporta system_instruction en config,
                    # o system role si se usa la API v1beta rest, pero SDK v0.x lo maneja en config
                    if system_instruction:
                         system_instruction += "\n" + content
                    else:
                         system_instruction = content
                elif role == "tool":
                     # Respuesta de tool
                     # Gemini espera role='tool' y partes con function_response
                     # OpenAI: content es JSON string, tool_call_id es ID
                     # Necesitamos reconstruir la parte de function response
                     # Nota: En la implementación simple, asumiremos que el historial 
                     # ya viene con el formato correcto o lo adaptamos.
                     # Para simplificar la interoperabilidad, procesaremos esto con cuidado.
                     
                     # Hack: si es tool response, el SDK de Gemini espera un formato específico.
                     # Por ahora, si estamos en modo Gemini, asumiremos que convertimos
                     # los mensajes de historial de OpenAI a Gemini "Parts".
                     
                     # Si el mensaje es simple texto:
                     gemini_contents.append(types.Content(
                         role="user" if role == "tool" else role, # 'tool' role en Gemini es específico
                         parts=[types.Part.from_text(text=f"[Tool Response] {content}")] 
                     ))
                     # TODO: Implementar conversión nativa de Tool Response si es crítico
                else:
                     # user o assistant
                     gemini_role = "user" if role == "user" else "model"
                     gemini_contents.append(types.Content(
                         role=gemini_role,
                         parts=[types.Part.from_text(text=str(content))]
                     ))

            # 2. Configurar tools
            gemini_tools = None
            gemini_tool_config = None
            
            if tools:
                # Convertir definiciones de tools OpenAI a Gemini
                # tools = [{"type": "function", "function": {...}}]
                function_declarations = []
                for t in tools:
                    if t.get("type") == "function":
                        func_def = t["function"]
                        # Crear FunctionDeclaration
                        # Nota: types.FunctionDeclaration toma parameters como Schema
                        # Esto requiere mapeo del JSON schema. 
                        # Para simplificar, pasamos el dict directamente si el SDK lo permite
                        # o construimos un objeto compatible.
                        
                        # El SDK google-genai suele aceptar dicts si coinciden con la estructura
                        function_declarations.append(func_def)
                
                if function_declarations:
                    gemini_tools = [types.Tool(function_declarations=function_declarations)]
                    gemini_tool_config = types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(
                            mode="AUTO" if not tool_choice or tool_choice == "auto" else "ANY"
                        )
                    )

            # 3. Configuración de generación
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=1.0, # Default para chat
                max_output_tokens=65536,
                tools=gemini_tools,
                tool_config=gemini_tool_config,
                thinking_config=types.ThinkingConfig(include_thoughts=True) if "gemini-3" in self.model or "thinking" in self.model else None
            )

            # 4. Llamada a la API (usando aio)
            # Usamos client.aio.models.generate_content
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=gemini_contents,
                config=config
            )
            
            return response

        except Exception as e:
            logger.error(f"Error en completion Gemini ({context}): {str(e)}")
            raise

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
        """
        if not self._ensure_client():
            return "Lo siento, el servicio de IA no está configurado."
        
        if not user_message or not user_message.strip():
            return "Por favor, envía un mensaje válido."
        
        if conversation_history is None:
            conversation_history = []
        
        # Lógica específica según proveedor
        if self.provider == "gemini":
            return await self._process_message_gemini(user_message, phone_number, conversation_history)
        else:
            return await self._process_message_openai(user_message, phone_number, conversation_history)

    async def _process_message_openai(self, user_message, phone_number, conversation_history):
        # ... (Lógica original de OpenAI) ...
        # Copiada del process_message original pero encapsulada
        
        # Construir mensajes
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        for msg in conversation_history[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})
        
        try:
            tools = self.get_tools()
            logger.debug(f"Llamando a OpenAI con modelo {self.model}")
            
            response = await self._create_chat_completion(
                messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                context="primary"
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    return "Error procesando argumentos de función."
                
                # Ejecutar función
                try:
                    function_result = await self._call_function(function_name, function_args)
                except Exception as e:
                    function_result = {"success": False, "error": str(e)}
                
                
                # Agregar el mensaje del asistente con la llamada a la función
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(function_result, default=self._json_default)
                })
                
                final_response = await self._create_chat_completion(messages, context="post_function")
                return final_response.choices[0].message.content
            else:
                return message.content
                
        except Exception as e:
            logger.error(f"Error en process_message_openai: {e}")
            return "Lo siento, ocurrió un error al procesar tu mensaje."

    async def _process_message_gemini(self, user_message, phone_number, conversation_history):
        # Lógica para Gemini
        
        # Construir mensajes (lista plana para el helper que los convierte luego)
        # Nota: Para Gemini, system prompt se maneja aparte, pero lo pasamos en la lista
        # y _create_gemini_completion lo extraerá.
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        for msg in conversation_history[-10:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})
        
        try:
            tools = self.get_tools()
            logger.debug(f"Llamando a Gemini con modelo {self.model}")
            print(f"[AGENT] Llamando a Gemini - Modelo: {self.model}", flush=True)
            
            response = await self._create_gemini_completion(
                messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                context="primary"
            )
            
            # Analizar respuesta
            # Gemini response tiene candidates[0].content.parts...
            # O response.text si es texto simple
            
            # Verificar si hay llamadas a función
            # En SDK google-genai, response.function_calls puede estar disponible o en parts
            
            # Acceder a la primera parte
            if not response.candidates or not response.candidates[0].content.parts:
                 return "No se recibió respuesta del modelo."

            parts = response.candidates[0].content.parts
            function_calls = [p.function_call for p in parts if p.function_call]
            
            if function_calls:
                fc = function_calls[0]
                function_name = fc.name
                function_args = fc.args # Esto ya es un dict usualmente
                
                # Ejecutar función
                try:
                    # function_args podría ser un objeto Map/Struct, convertir a dict si es necesario
                    if hasattr(function_args, "items"): 
                        args_dict = {k: v for k, v in function_args.items()}
                    else:
                        args_dict = function_args # Asumir dict
                        
                    function_result = await self._call_function(function_name, args_dict)
                except Exception as e:
                    function_result = {"success": False, "error": str(e)}
                
                # Segunda llamada con el resultado
                # Para Gemini, necesitamos pasar historial + llamada + respuesta
                
                # Agregamos la respuesta del modelo (function call) al historial de mensajes
                # Nota: Esto es delicado porque _create_gemini_completion reconstruye desde messages
                # Necesitamos simular el formato OpenAI para que _create_gemini_completion lo entienda
                # O construir los Contents manualmente aquí.
                
                # Simplificación: Agregamos mensaje de asistente con tool call (simulado)
                messages.append({
                    "role": "assistant", 
                    "content": f"Function Call: {function_name}({args_dict})" 
                })
                # Agregamos resultado
                messages.append({
                    "role": "user", # Usamos user para simular respuesta de tool en este esquema simple
                    "content": f"Function Result: {json.dumps(function_result, default=self._json_default)}"
                })
                
                print(f"[AGENT] Haciendo segunda llamada a Gemini después de función", flush=True)
                final_response = await self._create_gemini_completion(
                    messages, 
                    context="post_function"
                )
                
                # Asumimos respuesta de texto final
                return final_response.text if final_response.text else "Completado."
            
            else:
                return response.text

        except Exception as e:
            logger.error(f"Error en process_message_gemini: {e}")
            traceback.print_exc()
            return "Lo siento, ocurrió un error al procesar tu mensaje con Gemini."

    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna las herramientas disponibles para el agente"""
        raise NotImplementedError("Subclases deben implementar get_tools")


class OnboardingAgent(Agent):
    """Agente de onboarding para registrar nuevos usuarios"""
    
    def __init__(self):
        system_prompt = get_system_prompt(
            "onboarding_agent",
            """Eres un asistente amigable y entusiasta especializado en onboarding de nuevos usuarios.

Tu misión es ayudar a los usuarios a registrarse en el sistema de retos diarios. Debes:
1. Dar la bienvenida de manera cálida y personalizada
2. Pedir el nombre del usuario de forma natural
3. Entender sus intereses mediante una conversación fluida (no solo preguntar directamente)
4. Una vez que tengas nombre e intereses claros, usar la función register_user para registrarlos
5. Ser paciente y conversacional, no hacer sentir al usuario como si llenara un formulario

IMPORTANTE: Solo debes llamar a register_user cuando tengas tanto el nombre como los intereses del usuario claramente identificados. Si falta alguno, continúa la conversación de forma natural hasta obtenerlo."""
        )

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
        system_prompt = get_system_prompt(
            "dialogue_agent",
            """Eres un asistente motivador y cercano que apoya al usuario con el reto diario ya planificado.

Tu misión es:
1. Mantener conversaciones naturales y empáticas con usuarios registrados.
2. Resolver dudas sobre el reto diario asignado y ofrecer orientación práctica.
3. Motivar al usuario durante la ejecución del reto y animarlo a completarlo.
4. Registrar los avances, logros y feedback del usuario.
5. Detectar cambios de intereses o preferencias y actualizarlos con update_interests cuando corresponda.
6. Marcar retos como completados cuando el usuario lo indique.

IMPORTANTE:
- No generes ni inventes retos nuevos; el reto del día llega por otros medios.
- Refuerza el propósito del reto actual y su valor para el usuario.
- Adapta tu lenguaje al estilo y estado de ánimo del usuario.
- Sugiere recursos, recordatorios o ajustes útiles, pero siempre relacionados con el reto existente.
- Celebra los avances y crea confianza para que el usuario comparta su experiencia."""
        )

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

            challenges = user.get("challenges_sent") or []
            latest_challenge = None
            if isinstance(challenges, list) and challenges:
                latest_challenge = challenges[-1]

            latest_challenge_text = None
            latest_challenge_label = None
            if isinstance(latest_challenge, dict):
                latest_challenge_text = latest_challenge.get("question") or latest_challenge.get("text")
                latest_challenge_label = latest_challenge.get("sent_at") or latest_challenge.get("date")

            if latest_challenge_text:
                user_context += f"- Reto actual: {latest_challenge_text}\n"
                
                # Añadir opciones del reto
                if isinstance(latest_challenge, dict):
                    options = latest_challenge.get("options")
                    if options:
                        user_context += f"- Opciones: A) {options.get('A', '')}, B) {options.get('B', '')}, C) {options.get('C', '')}\n"
                    
                    # Añadir respuesta del usuario
                    user_answer = latest_challenge.get("user_answer")
                    if user_answer:
                        user_context += f"- Usuario eligió: {user_answer}\n"
                    
                    # Añadir respuesta correcta
                    correct_answer = latest_challenge.get("correct_answer")
                    if correct_answer:
                        user_context += f"- Respuesta correcta: {correct_answer}\n"

                    # Añadir estado
                    if latest_challenge.get("completed"):
                         user_context += "- Estado del reto: completado ✅\n"

            # Usar una copia del historial para no modificar el original si se usa en otro lado
            augmented_history = list(conversation_history[-10:])
            
            # Inyectar mensaje del reto si no está
            if latest_challenge_text:
                 # ... (Lógica de inyección de contexto visual del reto, opcional para el agente) ...
                 pass

            # Actualizar system prompt de la instancia (hack temporal para este request)
            original_system = self.system_prompt
            self.system_prompt = original_system + user_context
            
            try:
                # Delegar al padre (Agent.process_message) que maneja el ruteo por proveedor
                response = await super().process_message(user_message, phone_number, augmented_history)
            finally:
                # Restaurar system prompt
                self.system_prompt = original_system
                
            return response
        else:
            return "Parece que no estás registrado. Por favor, contacta al servicio de onboarding."

# Instancias globales
logger.info("Inicializando agentes...")
onboarding_agent = OnboardingAgent()
dialogue_agent = DialogueAgent()
logger.info("Agentes inicializados")
