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

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(title="WhatsApp IA Bot", version="1.0.0")

# Configurar OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OPENAI_API_KEY no encontrada. La IA no funcionará.")
else:
    client = AsyncOpenAI(api_key=openai_api_key)

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
        "service": "WhatsApp IA Bot",
        "connected": bot_state.is_connected
    }

@app.get("/health")
async def health_check():
    """Health check para producción"""
    return {
        "status": "healthy",
        "connected": bot_state.is_connected
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
                                if not openai_api_key:
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
    Genera una respuesta usando OpenAI
    """
    try:
        # Obtener contexto de la conversación si existe
        conversation_history = bot_state.active_conversations.get(phone_number, [])
        
        # Construir mensajes para OpenAI
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente útil y amigable en WhatsApp. Responde de manera concisa y natural."
            }
        ]
        
        # Agregar historial de conversación
        for msg in conversation_history[-5:]:  # Últimos 5 mensajes
            messages.append(msg)
        
        # Agregar el mensaje actual
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Llamar a OpenAI (usar el cliente si está configurado)
        if not openai_api_key:
            return "Lo siento, el servicio de IA no está configurado."
        
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Guardar en historial
        if phone_number not in bot_state.active_conversations:
            bot_state.active_conversations[phone_number] = []
        
        bot_state.active_conversations[phone_number].append({
            "role": "user",
            "content": user_message
        })
        bot_state.active_conversations[phone_number].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Limitar historial a 10 mensajes
        if len(bot_state.active_conversations[phone_number]) > 10:
            bot_state.active_conversations[phone_number] = bot_state.active_conversations[phone_number][-10:]
        
        return ai_response
    
    except Exception as e:
        logger.error(f"Error generando respuesta IA: {str(e)}")
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
    logger.info("Iniciando servidor WhatsApp IA Bot...")
    bot_state.is_connected = True
    logger.info("Servidor listo para recibir mensajes")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al apagar el servidor"""
    logger.info("Cerrando servidor...")
    bot_state.is_connected = False

if __name__ == "__main__":
    import uvicorn
    # Cloud Run inyecta PORT automáticamente, usar 8080 por defecto
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

