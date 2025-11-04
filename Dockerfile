# Dockerfile para Google Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Exponer puerto (Cloud Run usa PORT variable de entorno)
EXPOSE 8080

# Comando para ejecutar la aplicación
# Cloud Run inyecta PORT automáticamente, pero usamos 8080 como fallback
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}

