"""
Cliente para integrar con WhatsApp
Soporta múltiples métodos: Twilio, WhatsApp Business API, etc.
"""
import os
import logging
from typing import Optional
import aiohttp
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WhatsAppClient:
    """Cliente para enviar mensajes por WhatsApp"""
    
    def __init__(self):
        self.provider = os.getenv("WHATSAPP_PROVIDER", "meta")  # meta (oficial), twilio, etc.
        self.api_key = os.getenv("WHATSAPP_API_KEY")  # Para Meta: Access Token
        self.api_secret = os.getenv("WHATSAPP_API_SECRET")
        self.from_number = os.getenv("WHATSAPP_FROM_NUMBER")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")  # Requerido para Meta
        
    async def send_message(self, to: str, message: str) -> bool:
        """
        Envía un mensaje de WhatsApp
        
        Args:
            to: Número de teléfono destino (formato: +1234567890)
            message: Texto del mensaje
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            if self.provider == "twilio":
                return await self._send_via_twilio(to, message)
            elif self.provider == "meta":
                return await self._send_via_meta(to, message)
            else:
                logger.warning(f"Proveedor {self.provider} no implementado")
                return False
        except Exception as e:
            logger.error(f"Error enviando mensaje: {str(e)}")
            return False
    
    async def _send_via_twilio(self, to: str, message: str) -> bool:
        """Envía mensaje usando Twilio API"""
        if not self.api_key or not self.api_secret:
            logger.error("Twilio credentials no configuradas")
            return False
        
        account_sid = self.api_key
        auth_token = self.api_secret
        from_whatsapp = self.from_number or f"whatsapp:+{account_sid.split(':')[0]}"
        to_whatsapp = f"whatsapp:{to}"
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(account_sid, auth_token)
            data = {
                "From": from_whatsapp,
                "To": to_whatsapp,
                "Body": message
            }
            
            async with session.post(url, auth=auth, data=data) as response:
                if response.status == 201:
                    logger.info(f"Mensaje enviado a {to} via Twilio")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Error Twilio: {response.status} - {error_text}")
                    return False
    
    async def _send_via_meta(self, to: str, message: str) -> bool:
        """Envía mensaje usando Meta WhatsApp Business API oficial"""
        if not self.api_key:
            logger.error("Meta Access Token no configurado (WHATSAPP_API_KEY)")
            return False
        
        # Usar valor por defecto si no está configurado (para desarrollo)
        phone_number_id = self.phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID", "378914085314990")
        
        if not phone_number_id:
            logger.error("Phone Number ID no configurado (WHATSAPP_PHONE_NUMBER_ID)")
            return False
        
        access_token = self.api_key
        # phone_number_id ya está definido arriba con valor por defecto
        
        # Usar la versión más reciente de la API (v21.0)
        url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Formato del número: sin el símbolo +
        to_number = to.replace("+", "").strip()
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,  # Desactivar preview de URLs por defecto
                "body": message
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        message_id = response_data.get("messages", [{}])[0].get("id", "unknown")
                        logger.info(f"Mensaje enviado a {to} via Meta (ID: {message_id})")
                        return True
                    else:
                        error_message = response_data.get("error", {}).get("message", "Error desconocido")
                        error_code = response_data.get("error", {}).get("code", response.status)
                        logger.error(f"Error Meta API: {error_code} - {error_message}")
                        logger.debug(f"Payload enviado: {payload}")
                        return False
        except Exception as e:
            logger.error(f"Excepción al enviar mensaje via Meta: {str(e)}")
            return False

# Instancia global
whatsapp_client = WhatsAppClient()

