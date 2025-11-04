# 🚀 Guía de Despliegue GRATIS - Paso a Paso

## Opción 1: Railway (Más Fácil) ⭐ RECOMENDADO

### Paso 1: Crear cuenta
1. Ve a [railway.app](https://railway.app)
2. Click en **"Start a New Project"**
3. Inicia sesión con **GitHub** (necesitas tener cuenta de GitHub)

### Paso 2: Subir código a GitHub
```bash
# En tu terminal, desde la carpeta del proyecto:
git init
git add .
git commit -m "WhatsApp IA Bot"

# Crea un repositorio en github.com (nuevo repositorio)
# Luego conecta:
git remote add origin https://github.com/tu-usuario/tu-repo.git
git branch -M main
git push -u origin main
```

### Paso 3: Desplegar en Railway
1. En Railway Dashboard → **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Elige tu repositorio
4. Railway detectará automáticamente que es Python

### Paso 4: Configurar variables de entorno
En Railway Dashboard → Tu proyecto → **Variables**:

Agrega estas variables (copia desde tu `.env`):
```
OPENAI_API_KEY=tu_openai_api_key_aqui
OPENAI_MODEL=gpt-3.5-turbo
WHATSAPP_PROVIDER=meta
WHATSAPP_API_KEY=tu_whatsapp_access_token_aqui
WHATSAPP_PHONE_NUMBER_ID=378914085314990
WHATSAPP_VERIFY_TOKEN=whatsapp_webhook_verify_token_2024
WHATSAPP_BUSINESS_ACCOUNT_ID=453485421175530
PORT=8000
```

### Paso 5: Obtener tu URL
1. Railway te dará una URL automáticamente
2. Ejemplo: `https://tu-app.up.railway.app`
3. Esta es tu URL pública ✅

### Paso 6: Configurar webhook en Meta
1. Ve a Meta Dashboard → WhatsApp → Configuration
2. Webhook URL: `https://tu-app.up.railway.app/webhook/whatsapp`
3. Verify Token: `whatsapp_webhook_verify_token_2024`
4. Click en "Verificar y guardar"
5. Suscríbete a eventos: ✅ **messages**

### Paso 7: ¡Listo! 🎉
Tu bot está funcionando. Prueba enviando un mensaje a tu número de WhatsApp.

---

## Opción 2: Render (100% Gratis)

### Paso 1: Crear cuenta
1. Ve a [render.com](https://render.com)
2. Inicia sesión con **GitHub**

### Paso 2: Subir código a GitHub
(Mismo proceso que Railway arriba)

### Paso 3: Crear Web Service
1. En Render Dashboard → **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configuración:
   - **Name**: `whatsapp-ia-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Paso 4: Variables de entorno
En la sección **Environment**, agrega las mismas variables que en Railway.

### Paso 5: Desplegar
1. Click en **"Create Web Service"**
2. Render empezará a construir y desplegar
3. Te dará una URL: `https://whatsapp-ia-bot.onrender.com`

### Paso 6: Configurar webhook
(Mismo proceso que Railway, pero con la URL de Render)

### ⚠️ Nota sobre Render
- El servicio puede "dormir" después de 15 min de inactividad
- Se despierta automáticamente cuando llega un mensaje (~30 seg)
- Para WhatsApp esto está bien, los usuarios no notarán la diferencia

---

## 🆓 Costos

### Railway
- **$5 crédito gratis/mes** (suficiente para tu bot)
- Después cobra por uso (~$0.01/GB hora)
- **Estimado**: $0-2/mes (probablemente gratis)

### Render
- **Completamente gratis** en plan free
- Sin límites de tiempo
- Solo "sleep" después de inactividad

---

## ✅ Verificar que funciona

1. Visita: `https://tu-url.com/health`
   - Debe responder: `{"status": "healthy", "connected": true}`

2. Prueba el webhook:
```bash
curl https://tu-url.com/webhook/whatsapp/send?to=+34627191450&message=Hola
```

3. Envía un mensaje desde WhatsApp al número +34 627 19 14 50

---

## 🆘 Problemas Comunes

**Error: "Build failed"**
- Verifica que `requirements.txt` esté en el repositorio
- Revisa los logs de build en Railway/Render

**Error: "Webhook verification failed"**
- Verifica que la URL sea correcta (con HTTPS)
- Verifica que el Verify Token coincida exactamente

**El bot no responde**
- Revisa los logs en Railway/Render Dashboard
- Verifica que las variables de entorno estén configuradas
- Asegúrate de que el webhook esté verificado en Meta

---

## 📞 ¿Necesitas ayuda?

Si tienes problemas con algún paso, puedo ayudarte con:
- Configurar GitHub
- Desplegar en Railway/Render
- Configurar el webhook
- Debuggear problemas

