"""
Script simple para verificar que el servidor puede iniciar
"""
import os
import sys

# Verificar que las dependencias estén instaladas
try:
    from fastapi import FastAPI
    from uvicorn import run
    print("✅ FastAPI importado correctamente")
except ImportError as e:
    print(f"❌ Error importando FastAPI: {e}")
    sys.exit(1)

# Verificar puerto
port = int(os.getenv("PORT", 8080))
print(f"✅ Puerto configurado: {port}")

# Crear app simple
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "Server starting"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print(f"🚀 Iniciando servidor en puerto {port}...")
    run(app, host="0.0.0.0", port=port)

