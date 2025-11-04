# 🚀 Guía Rápida de Despliegue desde Cursor

## Opción Más Rápida: Railway (Recomendado)

### Paso 1: Preparar el código
1. Asegúrate de tener todos los archivos en tu repositorio Git:
```bash
git init
git add .
git commit -m "Initial commit"
```

### Paso 2: Crear cuenta en Railway
1. Ve a [railway.app](https://railway.app)
2. Inicia sesión con GitHub
3. Click en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Conecta tu repositorio

### Paso 3: Configurar Variables de Entorno
En Railway Dashboard, ve a tu proyecto → Variables y agrega:

```
OPENAI_API_KEY=tu_clave_de_openai_aqui
OPENAI_MODEL=gpt-3.5-turbo
```

### Paso 4: ¡Listo!
Railway detectará automáticamente que es Python y desplegará tu aplicación.
Obtendrás una URL como: `https://tu-app.railway.app`

### Paso 5: Configurar WhatsApp Webhook
- **Twilio**: Configura el webhook en Twilio Console → `https://tu-app.railway.app/webhook/whatsapp`
- **Meta**: Configura el webhook en Meta Business → `https://tu-app.railway.app/webhook/whatsapp`

---

## Alternativa: Render

### Paso 1: Crear cuenta
1. Ve a [render.com](https://render.com)
2. Inicia sesión con GitHub

### Paso 2: Crear Web Service
1. Click en "New +" → "Web Service"
2. Conecta tu repositorio
3. Configuración:
   - **Name**: `whatsapp-ia-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Paso 3: Variables de Entorno
En la sección "Environment", agrega:
```
OPENAI_API_KEY=tu_clave_aqui
```

### Paso 4: Deploy
Click en "Create Web Service"

---

## Alternativa: Heroku (desde terminal)

### Paso 1: Instalar Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku
```

### Paso 2: Login
```bash
heroku login
```

### Paso 3: Crear app
```bash
heroku create tu-app-nombre
```

### Paso 4: Configurar variables
```bash
heroku config:set OPENAI_API_KEY=tu_clave_aqui
```

### Paso 5: Deploy
```bash
git push heroku main
```

---

## Probar Localmente Primero

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Crear archivo .env
```bash
OPENAI_API_KEY=tu_clave_aqui
PORT=8000
```

### 3. Ejecutar servidor
```bash
python main.py
```

### 4. Probar
```bash
python test_local.py
```

O visita: http://localhost:8000

---

## ⚠️ Importante

1. **OPENAI_API_KEY**: Necesitas una clave de API de OpenAI. Obtén una en [platform.openai.com](https://platform.openai.com/api-keys)

2. **WhatsApp**: Para producción, necesitas:
   - **Twilio** (más fácil para empezar): [twilio.com/whatsapp](https://www.twilio.com/whatsapp)
   - **Meta WhatsApp Business API** (oficial, más complejo)

3. **HTTPS**: Las plataformas de despliegue proporcionan HTTPS automáticamente

4. **Webhooks**: Asegúrate de que tu URL de webhook sea accesible públicamente

---

## 🔍 Verificar que funciona

1. Visita: `https://tu-url.com/health`
   - Debe devolver: `{"status": "healthy", "connected": true}`

2. Prueba el webhook:
```bash
curl -X POST https://tu-url.com/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"from_number": "+1234567890", "message": "Hola"}'
```

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en la plataforma de despliegue
2. Verifica que las variables de entorno estén configuradas
3. Asegúrate de que el webhook de WhatsApp apunte a la URL correcta

