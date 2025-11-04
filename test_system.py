"""
Script de prueba para verificar que el sistema está configurado correctamente
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_system():
    """Prueba los componentes del sistema"""
    print("=" * 60)
    print("🧪 Probando sistema de retos diarios")
    print("=" * 60)
    
    # Test 1: Importaciones
    print("\n1️⃣ Verificando importaciones...")
    try:
        from database import database
        print("   ✅ database.py importado correctamente")
    except Exception as e:
        print(f"   ❌ Error importando database: {e}")
        return
    
    try:
        from agents import onboarding_agent, dialogue_agent
        print("   ✅ agents.py importado correctamente")
    except Exception as e:
        print(f"   ❌ Error importando agents: {e}")
        return
    
    try:
        from whatsapp_client import whatsapp_client
        print("   ✅ whatsapp_client.py importado correctamente")
    except Exception as e:
        print(f"   ❌ Error importando whatsapp_client: {e}")
        return
    
    # Test 2: Conexión a Firestore
    print("\n2️⃣ Verificando conexión a Firestore...")
    if database.is_connected():
        print("   ✅ Firestore conectado correctamente")
    else:
        print("   ⚠️  Firestore no está conectado")
        print("   💡 Ejecuta: gcloud auth application-default login")
        print("   💡 Y configura: gcloud config set project TU_PROJECT_ID")
    
    # Test 3: OpenAI
    print("\n3️⃣ Verificando configuración de OpenAI...")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("   ✅ OPENAI_API_KEY configurada")
        if onboarding_agent.client:
            print("   ✅ Cliente OpenAI inicializado")
        else:
            print("   ⚠️  Cliente OpenAI no inicializado")
    else:
        print("   ⚠️  OPENAI_API_KEY no configurada")
    
    # Test 4: WhatsApp
    print("\n4️⃣ Verificando configuración de WhatsApp...")
    whatsapp_provider = os.getenv("WHATSAPP_PROVIDER", "meta")
    whatsapp_key = os.getenv("WHATSAPP_API_KEY")
    print(f"   Provider: {whatsapp_provider}")
    if whatsapp_key:
        print("   ✅ WHATSAPP_API_KEY configurada")
    else:
        print("   ⚠️  WHATSAPP_API_KEY no configurada")
    
    # Test 5: Funciones de base de datos
    print("\n5️⃣ Probando funciones de base de datos...")
    if database.is_connected():
        try:
            # Intentar obtener un usuario de prueba (no debería existir)
            test_user = await database.get_user("+1234567890")
            if test_user is None:
                print("   ✅ Función get_user funciona correctamente")
            else:
                print("   ✅ Función get_user funciona (usuario encontrado)")
        except Exception as e:
            print(f"   ⚠️  Error probando get_user: {e}")
    else:
        print("   ⏭️  Saltando (Firestore no conectado)")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("=" * 60)
    print("\n📝 Próximos pasos:")
    print("   1. Configura Firestore si no está conectado")
    print("   2. Configura OPENAI_API_KEY si falta")
    print("   3. Configura las variables de WhatsApp")
    print("   4. Ejecuta: python main.py")
    print()

if __name__ == "__main__":
    asyncio.run(test_system())

