"""
Script helper para configurar variables de entorno
"""
import os

def setup_env():
    """Guía interactiva para configurar .env"""
    print("🔑 Configuración de API Key de OpenAI")
    print("=" * 50)
    print()
    print("Para obtener tu API Key:")
    print("1. Ve a https://platform.openai.com/api-keys")
    print("2. Inicia sesión o crea una cuenta")
    print("3. Click en 'Create new secret key'")
    print("4. Copia la clave (solo se muestra una vez)")
    print()
    
    api_key = input("Pega tu OpenAI API Key aquí: ").strip()
    
    if not api_key:
        print("❌ No se ingresó ninguna clave")
        return
    
    # Leer .env existente si existe
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Actualizar OPENAI_API_KEY
    env_vars['OPENAI_API_KEY'] = api_key
    env_vars['OPENAI_MODEL'] = env_vars.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    env_vars['PORT'] = env_vars.get('PORT', '8000')
    
    # Escribir .env
    with open('.env', 'w') as f:
        f.write("# OpenAI Configuration\n")
        f.write(f"OPENAI_API_KEY={env_vars['OPENAI_API_KEY']}\n")
        f.write(f"OPENAI_MODEL={env_vars['OPENAI_MODEL']}\n")
        f.write("\n# Server Configuration\n")
        f.write(f"PORT={env_vars['PORT']}\n")
        f.write("\n# WhatsApp Configuration (opcional)\n")
        f.write("# WHATSAPP_PROVIDER=twilio\n")
        f.write("# WHATSAPP_API_KEY=\n")
        f.write("# WHATSAPP_API_SECRET=\n")
        f.write("# WHATSAPP_FROM_NUMBER=\n")
    
    print()
    print("✅ Archivo .env creado/actualizado correctamente")
    print("⚠️  IMPORTANTE: El archivo .env está en .gitignore y NO se subirá a Git")
    print()
    print("Ahora puedes ejecutar: python main.py")

if __name__ == "__main__":
    setup_env()

