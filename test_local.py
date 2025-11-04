"""
Script de prueba local para el bot de WhatsApp
Útil para probar la integración sin necesidad de WhatsApp
"""
import asyncio
import aiohttp
import json

async def test_local():
    """Prueba el servidor local"""
    base_url = "http://localhost:8000"
    
    # Probar health check
    print("🔍 Probando health check...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/health") as response:
            print(f"✅ Health: {await response.json()}")
    
    # Probar recepción de mensaje
    print("\n📨 Probando recepción de mensaje...")
    test_message = {
        "from_number": "+1234567890",
        "message": "Hola, ¿cómo estás?",
        "message_id": "test_123"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{base_url}/webhook/whatsapp",
            json=test_message
        ) as response:
            result = await response.json()
            print(f"✅ Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas locales...")
    print("⚠️  Asegúrate de que el servidor esté corriendo (python main.py)")
    print()
    asyncio.run(test_local())

