"""
Script para probar la configuración de WhatsApp Meta API
"""
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_whatsapp_config():
    """Prueba la configuración de WhatsApp"""
    print("🔍 Verificando configuración de WhatsApp Meta API...")
    print("=" * 60)
    
    # Verificar variables de entorno
    api_key = os.getenv("WHATSAPP_API_KEY")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
    
    print(f"\n✅ Provider: {os.getenv('WHATSAPP_PROVIDER', 'meta')}")
    print(f"✅ Phone Number ID: {phone_number_id}")
    print(f"✅ Verify Token: {verify_token}")
    print(f"✅ Business Account ID: {business_account_id}")
    print(f"✅ API Key presente: {'Sí' if api_key else 'No'}")
    
    if not api_key or not phone_number_id:
        print("\n❌ Faltan credenciales esenciales")
        return
    
    # Probar conexión con Meta API
    print("\n🌐 Probando conexión con Meta API...")
    
    # Endpoint para verificar el número de teléfono
    url = f"https://graph.facebook.com/v21.0/{phone_number_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Conexión exitosa con Meta API")
                    print(f"   Número verificado: {data.get('verified_name', 'N/A')}")
                    print(f"   Display Name: {data.get('display_phone_number', 'N/A')}")
                elif response.status == 401:
                    print("❌ Error de autenticación")
                    print("   El Access Token puede haber expirado o ser inválido")
                    error_data = await response.json()
                    print(f"   Error: {error_data.get('error', {}).get('message', 'Desconocido')}")
                else:
                    error_data = await response.json()
                    print(f"❌ Error {response.status}: {error_data.get('error', {}).get('message', 'Desconocido')}")
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📝 Próximos pasos:")
    print("1. Despliega tu servidor (Railway, Render, etc.)")
    print("2. Configura el webhook en Meta Dashboard:")
    print(f"   URL: https://tu-dominio.com/webhook/whatsapp")
    print(f"   Verify Token: {verify_token}")
    print("3. Suscríbete a eventos: messages")
    print("4. ¡Prueba enviando un mensaje a tu número de WhatsApp Business!")

if __name__ == "__main__":
    asyncio.run(test_whatsapp_config())

