# Sistema de IA integrado con WhatsApp

Sistema de chatbot con IA para WhatsApp listo para producción.

## 🚀 Características

- **FastAPI** como servidor backend
- **OpenAI** para respuestas inteligentes
- **Webhooks** para recibir mensajes de WhatsApp
- **Memoria de conversación** para contexto
- **Listo para producción** con configuración para múltiples plataformas

## 📋 Requisitos Previos

- Python 3.9+
- Cuenta de OpenAI con API key
- Servicio de WhatsApp (Twilio, WhatsApp Business API, o similar)

## 🔧 Instalación Local

1. **Clonar e instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY
```

3. **Ejecutar el servidor:**
```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`

## 🌐 Despliegue en Producción

### Opción 1: Railway (Recomendado - Más fácil)

1. **Crear cuenta en [Railway](https://railway.app)**

2. **Conectar tu repositorio:**
   - Ve a Railway Dashboard
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Conecta tu repositorio

3. **Configurar variables de entorno:**
   - En Railway, ve a "Variables"
   - Agrega:
     - `OPENAI_API_KEY`: Tu clave de OpenAI
     - `PORT`: 8000 (Railway lo configura automáticamente)
     - `OPENAI_MODEL`: gpt-3.5-turbo (opcional)

4. **Railway detectará automáticamente Python y usará `requirements.txt`**

5. **Tu servidor estará disponible en una URL de Railway**

### Opción 2: Render

1. **Crear cuenta en [Render](https://render.com)**

2. **Crear nuevo Web Service:**
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub

3. **Configuración:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3

4. **Variables de entorno:**
   - Agrega `OPENAI_API_KEY` en la sección Environment

5. **Desplegar**

### Opción 3: Heroku

1. **Instalar Heroku CLI**

2. **Crear Procfile:**
```bash
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

3. **Desplegar:**
```bash
heroku create tu-app-nombre
heroku config:set OPENAI_API_KEY=tu_key
git push heroku main
```

### Opción 4: VPS propio (DigitalOcean, AWS, etc.)

1. **Conectar por SSH:**
```bash
ssh usuario@tu-servidor
```

2. **Instalar dependencias:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

3. **Clonar y configurar:**
```bash
git clone tu-repo
cd MindExplorer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configurar systemd service** (crear `/etc/systemd/system/whatsapp-bot.service`):
```ini
[Unit]
Description=WhatsApp IA Bot
After=network.target

[Service]
User=tu-usuario
WorkingDirectory=/ruta/a/MindExplorer
Environment="PATH=/ruta/a/MindExplorer/venv/bin"
ExecStart=/ruta/a/MindExplorer/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Iniciar servicio:**
```bash
sudo systemctl start whatsapp-bot
sudo systemctl enable whatsapp-bot
```

6. **Configurar Nginx como reverse proxy** (opcional pero recomendado)

## 📱 Integración con WhatsApp

### ✅ Configurado para Meta WhatsApp Business API (Oficial)

Este proyecto está **configurado por defecto** para usar la API oficial de Meta WhatsApp Business.

**📖 Ver guía completa de configuración:** [`META_SETUP.md`](META_SETUP.md)

#### Variables de entorno necesarias:

```bash
WHATSAPP_PROVIDER=meta
WHATSAPP_API_KEY=tu_access_token_de_meta
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_VERIFY_TOKEN=tu_token_secreto
WHATSAPP_APP_SECRET=tu_app_secret  # Opcional pero recomendado
```

#### Pasos rápidos:

1. Crea una App en [developers.facebook.com](https://developers.facebook.com)
2. Configura WhatsApp en tu App
3. Obtén tus credenciales (Access Token, Phone Number ID)
4. Configura el webhook en Meta Dashboard apuntando a: `https://tu-dominio.com/webhook/whatsapp`
5. Configura las variables de entorno en tu servidor

### Opción Alternativa: Twilio WhatsApp API

Si prefieres usar Twilio, cambia:
```bash
WHATSAPP_PROVIDER=twilio
WHATSAPP_API_KEY=tu_twilio_account_sid
WHATSAPP_API_SECRET=tu_twilio_auth_token
```

## 🔌 Endpoints API

### GET `/`
- Estado del servidor

### GET `/health`
- Health check para monitoreo

### GET `/webhook/whatsapp`
- **Verificación de webhook para Meta** (requerido por Meta)
- Query params: `hub.mode`, `hub.verify_token`, `hub.challenge`
- Meta llama automáticamente a este endpoint para verificar el webhook

### POST `/webhook/whatsapp`
- **Recibe webhooks de Meta WhatsApp Business API**
- Maneja mensajes entrantes automáticamente
- Formato de payload según especificación de Meta
- Valida firmas de webhook si `WHATSAPP_APP_SECRET` está configurado
- Responde automáticamente con IA y envía la respuesta a WhatsApp

### POST `/webhook/whatsapp/send`
- Envía mensajes de WhatsApp manualmente
- Query params: `to` (número con +), `message` (texto)
- Ejemplo: `/webhook/whatsapp/send?to=+1234567890&message=Hola`

## 🔒 Seguridad

- ✅ Usa HTTPS en producción
- ✅ Valida webhooks con firmas (Twilio, Meta)
- ✅ Limita rate limiting
- ✅ Protege tu API key de OpenAI

## 📝 Notas

- El historial de conversación se mantiene en memoria (se pierde al reiniciar)
- Para producción, considera usar Redis para persistencia
- Asegúrate de cumplir con las políticas de WhatsApp Business

## 🆘 Troubleshooting

**Error: OPENAI_API_KEY no encontrada**
- Verifica que hayas configurado la variable de entorno

**Error: Puerto ya en uso**
- Cambia el PORT en `.env` o usa otro puerto

**WhatsApp no recibe mensajes**
- Verifica que el webhook esté configurado correctamente
- Revisa los logs del servidor

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Twilio WhatsApp](https://www.twilio.com/whatsapp)
- [Railway Docs](https://docs.railway.app/)

