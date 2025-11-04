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
# Cloud Run inyecta PORT automáticamente como variable de entorno
# Usamos sh -c para asegurar que la variable PORT se expanda correctamente
# Cloud Run siempre inyecta PORT como variable de entorno
# Usar directamente $PORT sin fallback
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}

