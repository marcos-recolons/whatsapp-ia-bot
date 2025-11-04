"""
Versión simplificada para diagnosticar problemas de inicio
"""
import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(title="WhatsApp IA Bot", version="1.0.0")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "status": "online",
        "service": "WhatsApp IA Bot",
        "port": os.getenv("PORT", "8080")
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "port": os.getenv("PORT", "8080")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Iniciando servidor simplificado en puerto {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

