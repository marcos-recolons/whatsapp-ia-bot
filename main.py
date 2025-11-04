"""
Sistema de IA integrado con WhatsApp
Servidor FastAPI para producción
"""
import os
import logging
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
from openai import AsyncOpenAI
from whatsapp_client import whatsapp_client
from database import database
from agents import onboarding_agent, dialogue_agent

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Habilitar logging de nivel DEBUG para agentes
logging.getLogger("agents").setLevel(logging.DEBUG)

# Inicializar FastAPI
app = FastAPI(title="WhatsApp IA Bot", version="1.0.0")

# Configurar OpenAI (lazy initialization para evitar errores al importar)
openai_api_key = os.getenv("OPENAI_API_KEY")
client = None

def init_openai_client():
    """Inicializa el cliente de OpenAI solo cuando sea necesario"""
    global client
    if client is None and openai_api_key:
        try:
            client = AsyncOpenAI(api_key=openai_api_key)
            logger.info("OpenAI cliente inicializado correctamente")
        except Exception as e:
            logger.warning(f"Error inicializando OpenAI: {str(e)}")
            client = None
    return client

if not openai_api_key:
    logger.warning("OPENAI_API_KEY no encontrada. La IA no funcionará.")

# Modelos de datos
class WhatsAppMessage(BaseModel):
    from_number: str
    message: str
    message_id: Optional[str] = None

class AIResponse(BaseModel):
    response: str
    success: bool

# Modelos para Meta Webhook
class MetaWebhookEntry(BaseModel):
    id: str
    changes: list

class MetaWebhookPayload(BaseModel):
    object: Optional[str] = None
    entry: Optional[list] = None

# Estado del bot
class BotState:
    def __init__(self):
        self.is_connected = False
        self.active_conversations = {}

bot_state = BotState()

@app.get("/")
async def root():
    """Endpoint de salud"""
    return {
        "status": "online",
        "service": "WhatsApp IA Bot - Sistema de Retos Diarios",
        "connected": bot_state.is_connected,
        "database_connected": database.is_connected()
    }

@app.get("/health")
async def health_check():
    """Health check para producción"""
    return {
        "status": "healthy",
        "connected": bot_state.is_connected,
        "database_connected": database.is_connected()
    }

@app.get("/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    """
    Endpoint de verificación de webhook para Meta WhatsApp Business API
    Meta llama a este endpoint para verificar que eres el dueño del webhook
    """
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "whatsapp_webhook_verify_token_2024")
    
    if not verify_token:
        logger.error("WHATSAPP_VERIFY_TOKEN no configurado")
        raise HTTPException(status_code=500, detail="Webhook verify token no configurado")
    
    # Verificar el token
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info("Webhook verificado correctamente")
        return PlainTextResponse(hub_challenge)
    else:
        logger.warning(f"Fallo en verificación de webhook: mode={hub_mode}, token={hub_verify_token[:10]}...")
        raise HTTPException(status_code=403, detail="Token de verificación inválido")

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verifica la firma del webhook de Meta
    """
    app_secret = os.getenv("WHATSAPP_APP_SECRET")
    if not app_secret:
        logger.warning("WHATSAPP_APP_SECRET no configurado, saltando verificación de firma")
        return True  # Permitir si no está configurado
    
    # Meta usa HMAC SHA256
    expected_signature = hmac.new(
        app_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Meta envía la firma como "sha256=..."
    if signature.startswith("sha256="):
        signature = signature[7:]
    
    return hmac.compare_digest(expected_signature, signature)

@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="x-hub-signature-256")
):
    """
    Recibe webhooks de Meta WhatsApp Business API
    Maneja mensajes entrantes y genera respuestas con IA
    """
    try:
        # Leer el body completo para verificación de firma
        body_bytes = await request.body()
        
        # Verificar firma si está configurada
        if x_hub_signature_256:
            if not verify_webhook_signature(body_bytes, x_hub_signature_256):
                logger.warning("Firma de webhook inválida")
                raise HTTPException(status_code=403, detail="Firma inválida")
        
        # Parsear JSON desde bytes
        payload = json.loads(body_bytes.decode('utf-8'))
        logger.info(f"Webhook recibido: {payload}")
        
        # Procesar según formato de Meta
        if payload.get("object") == "whatsapp_business_account":
            entries = payload.get("entry", [])
            
            for entry in entries:
                changes = entry.get("changes", [])
                
                for change in changes:
                    value = change.get("value", {})
                    
                    # Procesar mensajes
                    if "messages" in value:
                        messages = value["messages"]
                        
                        for message in messages:
                            # Obtener información del mensaje
                            message_id = message.get("id")
                            message_type = message.get("type")
                            
                            # Solo procesar mensajes de texto
                            if message_type == "text":
                                message_text = message.get("text", {}).get("body", "")
                                from_number = message.get("from", "")
                                
                                logger.info(f"Mensaje recibido de {from_number}: {message_text}")
                                
                                # Generar respuesta con IA
                                ai_client = init_openai_client()
                                if not ai_client:
                                    response_text = "Lo siento, el servicio de IA no está configurado."
                                else:
                                    response_text = await generate_ai_response(message_text, from_number)
                                
                                # Enviar respuesta automáticamente a WhatsApp
                                if response_text:
                                    await whatsapp_client.send_message(from_number, response_text)
                                    logger.info(f"Respuesta enviada a {from_number}")
                            
                            # Manejar otros tipos de mensajes (imágenes, audio, etc.)
                            elif message_type in ["image", "audio", "video", "document"]:
                                logger.info(f"Mensaje de tipo {message_type} recibido, no procesado")
                                # Opcional: enviar mensaje de que solo se procesan textos
                                from_number = message.get("from", "")
                                await whatsapp_client.send_message(
                                    from_number,
                                    "Por ahora solo puedo procesar mensajes de texto. Por favor envía tu mensaje en texto."
                                )
        
        # Responder 200 OK a Meta
        return {"status": "ok"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        # Aún así responder 200 para que Meta no reintente constantemente
        return {"status": "error", "message": str(e)}

async def generate_ai_response(user_message: str, phone_number: str) -> str:
    """
    Genera una respuesta usando los agentes de IA
    Decide qué agente usar según si el usuario está registrado o no
    """
    try:
        # Obtener contexto de la conversación si existe
        conversation_history = bot_state.active_conversations.get(phone_number, [])
        
        # Verificar si el usuario existe en la base de datos
        user = await database.get_user(phone_number)
        
        # Verificar que los agentes estén inicializados
        if not onboarding_agent.client:
            logger.error("Agente de onboarding no tiene cliente OpenAI inicializado")
        if not dialogue_agent.client:
            logger.error("Agente de diálogo no tiene cliente OpenAI inicializado")
        
        # Si el usuario no existe o no ha completado el onboarding, usar agente de onboarding
        if not user or not user.get("onboarding_completed", False):
            logger.info(f"Usuario {phone_number} no registrado o en onboarding, usando agente de onboarding")
            logger.debug(f"Cliente onboarding disponible: {onboarding_agent.client is not None}")
            try:
                response_text = await onboarding_agent.process_message(
                    user_message, 
                    phone_number, 
                    conversation_history
                )
            except Exception as e:
                logger.error(f"Error en onboarding_agent.process_message: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                raise
            
            # Verificar si el usuario acaba de completar el onboarding
            user_after = await database.get_user(phone_number)
            if user_after and user_after.get("onboarding_completed", False):
                logger.info(f"Usuario {phone_number} completó el onboarding")
                # Opcional: mensaje de bienvenida al sistema de retos
                response_text += "\n\n¡Bienvenido al sistema de retos diarios! A partir de ahora recibirás retos personalizados basados en tus intereses."
        else:
            # Usuario registrado, usar agente de diálogo
            logger.info(f"Usuario {phone_number} registrado, usando agente de diálogo")
            logger.debug(f"Cliente diálogo disponible: {dialogue_agent.client is not None}")
            try:
                response_text = await dialogue_agent.process_message(
                    user_message,
                    phone_number,
                    conversation_history
                )
            except Exception as e:
                logger.error(f"Error en dialogue_agent.process_message: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                raise
        
        # Guardar en historial
        if phone_number not in bot_state.active_conversations:
            bot_state.active_conversations[phone_number] = []
        
        bot_state.active_conversations[phone_number].append({
            "role": "user",
            "content": user_message
        })
        bot_state.active_conversations[phone_number].append({
            "role": "assistant",
            "content": response_text
        })
        
        # Limitar historial a 20 mensajes (más que antes porque los agentes necesitan más contexto)
        if len(bot_state.active_conversations[phone_number]) > 20:
            bot_state.active_conversations[phone_number] = bot_state.active_conversations[phone_number][-20:]
        
        return response_text
    
    except Exception as e:
        logger.error(f"Error generando respuesta IA: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."

@app.post("/webhook/whatsapp/send")
async def send_whatsapp_message(to: str, message: str):
    """
    Endpoint para enviar mensajes de WhatsApp
    """
    try:
        logger.info(f"Enviando mensaje a {to}: {message}")
        
        success = await whatsapp_client.send_message(to, message)
        
        if success:
            return {
                "success": True,
                "message": "Mensaje enviado",
                "to": to
            }
        else:
            raise HTTPException(status_code=500, detail="Error enviando mensaje por WhatsApp")
    
    except Exception as e:
        logger.error(f"Error enviando mensaje: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar el servidor"""
    try:
        logger.info("=" * 60)
        logger.info("Iniciando servidor WhatsApp IA Bot...")
        logger.info(f"Puerto: {os.getenv('PORT', '8080')}")
        logger.info(f"OpenAI API Key presente: {'Sí' if openai_api_key else 'No'}")
        logger.info(f"WhatsApp provider: {os.getenv('WHATSAPP_PROVIDER', 'meta')}")
        logger.info(f"Firestore conectado: {'Sí' if database.is_connected() else 'No'}")
        bot_state.is_connected = True
        logger.info("✅ Servidor listo para recibir mensajes")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Error en startup: {str(e)}")
        # No lanzar excepción para que el servidor pueda iniciar

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al apagar el servidor"""
    logger.info("Cerrando servidor...")
    bot_state.is_connected = False

if __name__ == "__main__":
    import uvicorn
    # Cloud Run inyecta PORT automáticamente, usar 8080 por defecto
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Iniciando servidor en puerto {port}")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )

