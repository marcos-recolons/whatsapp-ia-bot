# 🚀 Pasos Inmediatos para Desplegar en Railway

## ✅ Lo que ya está hecho:
- ✅ Git inicializado
- ✅ Archivos preparados
- ✅ Commit inicial creado
- ✅ `.env` está en `.gitignore` (no se subirá)

## 📋 Ahora sigue estos pasos:

### 1️⃣ Crear repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Click en **"+"** (arriba derecha) → **"New repository"**
3. Nombre: `whatsapp-ia-bot` (o el que prefieras)
4. Descripción (opcional): "Bot de WhatsApp con IA"
5. **NO marques** "Add a README file" (ya tenemos uno)
6. **NO marques** "Add .gitignore" (ya tenemos uno)
7. Click en **"Create repository"**

### 2️⃣ Conectar y subir código

**Copia y pega estos comandos** (reemplaza `TU-USUARIO` con tu usuario de GitHub):

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer

# Conectar con tu repositorio de GitHub
git remote add origin https://github.com/TU-USUARIO/whatsapp-ia-bot.git

# Cambiar a rama main
git branch -M main

# Subir código
git push -u origin main
```

**Si te pide autenticación:**
- Usa tu **Personal Access Token** de GitHub (no tu contraseña)
- O instala GitHub CLI: `brew install gh` y luego `gh auth login`

### 3️⃣ Desplegar en Railway

1. Ve a [railway.app](https://railway.app)
2. Click en **"Start a New Project"** o **"Login"**
3. Selecciona **"Login with GitHub"**
4. Autoriza Railway
5. Click en **"New Project"**
6. Selecciona **"Deploy from GitHub repo"**
7. Elige tu repositorio `whatsapp-ia-bot`
8. **¡Railway empezará a desplegar automáticamente!**

### 4️⃣ Configurar Variables de Entorno

**IMPORTANTE**: Railway necesita estas variables para funcionar.

1. En Railway Dashboard → Tu proyecto → Click en el servicio
2. Ve a la pestaña **"Variables"** (o "Environment")
3. Click en **"New Variable"** o **"Raw Editor"**

**Copia y pega esto** (cambia a modo "Raw Editor" si está disponible):

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

**O agrégalas una por una** si prefieres:
- Name: `OPENAI_API_KEY`, Value: `tu_openai_api_key_aqui`
- Name: `WHATSAPP_API_KEY`, Value: `tu_whatsapp_access_token_aqui`
- etc.

### 5️⃣ Obtener tu URL

1. En Railway Dashboard → Tu proyecto
2. Click en **"Settings"** → **"Generate Domain"**
3. O busca la sección **"Domains"**
4. Railway te dará una URL como: `https://whatsapp-ia-bot-production.up.railway.app`
5. **¡Copia esta URL!** La necesitarás para el webhook

### 6️⃣ Configurar Webhook en Meta

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Selecciona tu App → **WhatsApp** → **Configuration**
3. En **Webhook**, click en **"Edit"**
4. **Callback URL**: `https://tu-url-de-railway.up.railway.app/webhook/whatsapp`
   (Pega tu URL real de Railway + `/webhook/whatsapp`)
5. **Verify Token**: `whatsapp_webhook_verify_token_2024`
6. Click en **"Verify and Save"**
7. ✅ Deberías ver "Webhook verified"

### 7️⃣ Suscribirse a eventos

En la misma página:
- Marca ✅ **messages**
- (Opcional) ✅ **message_status**

### 8️⃣ ¡Probar!

1. Abre WhatsApp
2. Envía mensaje a: **+34 627 19 14 50**
3. El bot debería responder 🎉

---

## 🔍 Verificar que funciona

Visita en tu navegador:
```
https://tu-url-de-railway.up.railway.app/health
```

Deberías ver:
```json
{"status": "healthy", "connected": true}
```

---

## ⏱️ Tiempo estimado

- Crear repo GitHub: 2 min
- Subir código: 2 min
- Desplegar en Railway: 3-5 min
- Configurar variables: 5 min
- Configurar webhook: 3 min
- **Total: ~15-20 minutos**

---

## 🆘 ¿Problemas?

Dime en qué paso estás y qué error ves, y te ayudo a resolverlo.

