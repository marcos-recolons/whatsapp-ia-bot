#!/usr/bin/env python3
"""
Script para diagnosticar errores en los agentes
"""
import asyncio
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_agent():
    """Prueba los agentes con un mensaje de prueba"""
    print("=" * 60)
    print("🔍 Diagnóstico de Agentes")
    print("=" * 60)
    
    # Verificar variables de entorno
    print("\n1️⃣ Verificando variables de entorno...")
    openai_key = os.getenv("OPENAI_API_KEY")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    print(f"   OPENAI_API_KEY: {'✅ Configurada' if openai_key else '❌ No configurada'}")
    print(f"   GOOGLE_CLOUD_PROJECT: {project_id or 'No configurado'}")
    print(f"   OPENAI_MODEL: {model}")
    
    if not openai_key:
        print("\n❌ OPENAI_API_KEY no está configurada")
        return
    
    # Verificar Firestore
    print("\n2️⃣ Verificando Firestore...")
    try:
        from database import database
        if database.is_connected():
            print("   ✅ Firestore conectado")
        else:
            print("   ⚠️  Firestore no conectado")
    except Exception as e:
        print(f"   ❌ Error importando database: {e}")
        import traceback
        traceback.print_exc()
    
    # Verificar agentes
    print("\n3️⃣ Verificando agentes...")
    try:
        from agents import onboarding_agent, dialogue_agent
        
        print(f"   Onboarding agent cliente: {'✅' if onboarding_agent.client else '❌'}")
        print(f"   Dialogue agent cliente: {'✅' if dialogue_agent.client else '❌'}")
        print(f"   Modelo onboarding: {onboarding_agent.model}")
        print(f"   Modelo diálogo: {dialogue_agent.model}")
        
        # Verificar tools
        onboarding_tools = onboarding_agent.get_tools()
        dialogue_tools = dialogue_agent.get_tools()
        print(f"   Tools onboarding: {len(onboarding_tools)}")
        print(f"   Tools diálogo: {len(dialogue_tools)}")
        
    except Exception as e:
        print(f"   ❌ Error importando agentes: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Probar con un mensaje simple
    print("\n4️⃣ Probando agente de onboarding con mensaje de prueba...")
    test_phone = "+1234567890"
    test_message = "Hola"
    
    try:
        response = await onboarding_agent.process_message(
            test_message,
            test_phone,
            []
        )
        print(f"   ✅ Respuesta recibida: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico completado")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent())

