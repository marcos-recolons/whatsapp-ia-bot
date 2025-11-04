# 🚂 Guía Paso a Paso: Desplegar en Railway

## ✅ Paso 1: Crear cuenta en GitHub (si no tienes)

1. Ve a [github.com](https://github.com) y crea una cuenta
2. O inicia sesión si ya tienes una

## ✅ Paso 2: Crear repositorio en GitHub

1. En GitHub, click en **"+"** → **"New repository"**
2. Nombre: `whatsapp-ia-bot` (o el que prefieras)
3. **NO marques** "Initialize with README" (ya tenemos archivos)
4. Click en **"Create repository"**

## ✅ Paso 3: Subir código a GitHub

**Ya tienes Git inicializado aquí.** Ahora ejecuta estos comandos:

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer

# Hacer commit inicial
git commit -m "Initial commit: WhatsApp IA Bot"

# Conectar con GitHub (reemplaza TU-USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU-USUARIO/whatsapp-ia-bot.git

# Cambiar a rama main
git branch -M main

# Subir código
git push -u origin main
```

**Nota**: Necesitarás autenticarte con GitHub. Si te pide credenciales:
- Puedes usar un **Personal Access Token** en lugar de contraseña
- O usar GitHub CLI: `gh auth login`

## ✅ Paso 4: Crear cuenta en Railway

1. Ve a [railway.app](https://railway.app)
2. Click en **"Start a New Project"** o **"Login"**
3. Selecciona **"Login with GitHub"**
4. Autoriza Railway a acceder a tus repositorios

## ✅ Paso 5: Desplegar proyecto

1. En Railway Dashboard → **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Elige tu repositorio `whatsapp-ia-bot`
4. Railway empezará a desplegar automáticamente

**Espera 2-3 minutos** mientras Railway:
- Detecta que es Python
- Instala dependencias desde `requirements.txt`
- Inicia el servidor

## ✅ Paso 6: Configurar Variables de Entorno

1. En Railway Dashboard → Tu proyecto → Click en el servicio
2. Ve a la pestaña **"Variables"**
3. Click en **"New Variable"** y agrega cada una:

```
OPENAI_API_KEY
tu_openai_api_key_aqui
```

```
OPENAI_MODEL
gpt-3.5-turbo
```

```
WHATSAPP_PROVIDER
meta
```

```
WHATSAPP_API_KEY
tu_whatsapp_access_token_aqui
```

```
WHATSAPP_PHONE_NUMBER_ID
378914085314990
```

```
WHATSAPP_VERIFY_TOKEN
whatsapp_webhook_verify_token_2024
```

```
WHATSAPP_BUSINESS_ACCOUNT_ID
453485421175530
```

```
PORT
8000
```

## ✅ Paso 7: Obtener tu URL pública

1. En Railway Dashboard → Tu proyecto
2. Click en la pestaña **"Settings"**
3. Busca **"Domains"** o **"Generate Domain"**
4. Railway te dará una URL como: `https://tu-app.up.railway.app`
5. **Copia esta URL** - la necesitarás para el webhook

## ✅ Paso 8: Configurar Webhook en Meta

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Selecciona tu App → **WhatsApp** → **Configuration**
3. En **Webhook**, click en **"Edit"** o **"Configure"**
4. **Callback URL**: `https://tu-app.up.railway.app/webhook/whatsapp`
   (Reemplaza con tu URL real de Railway)
5. **Verify Token**: `whatsapp_webhook_verify_token_2024`
6. Click en **"Verify and Save"**
7. Deberías ver un ✅ verde que dice "Webhook verified"

## ✅ Paso 9: Suscribirse a eventos

En la misma página de configuración de webhook:
- Marca ✅ **messages**
- (Opcional) Marca ✅ **message_status**

## ✅ Paso 10: ¡Probar!

1. Abre WhatsApp en tu teléfono
2. Envía un mensaje al número: **+34 627 19 14 50**
3. El bot debería responder automáticamente 🎉

## 🔍 Verificar que funciona

### Probar endpoint de salud:
Visita en tu navegador:
```
https://tu-app.up.railway.app/health
```

Deberías ver:
```json
{"status": "healthy", "connected": true}
```

### Ver logs en Railway:
1. En Railway Dashboard → Tu proyecto
2. Click en la pestaña **"Deployments"** o **"Logs"**
3. Verás los logs en tiempo real

## 🆘 Problemas Comunes

**Error: "Build failed"**
- Verifica que `requirements.txt` esté en el repositorio
- Revisa los logs de build en Railway

**Error: "Webhook verification failed"**
- Verifica que la URL sea correcta (con HTTPS)
- Verifica que el Verify Token coincida exactamente
- Asegúrate de que Railway haya terminado de desplegar

**El bot no responde**
- Revisa los logs en Railway (pestaña "Logs")
- Verifica que todas las variables de entorno estén configuradas
- Asegúrate de que el webhook esté verificado (✅ verde en Meta)

**"Application error" o "502 Bad Gateway"**
- Revisa los logs - probablemente falta una variable de entorno
- Verifica que `PORT` esté configurado (Railway lo inyecta automáticamente)

## 💡 Tips

- Railway te da **$5 de crédito gratis/mes** - suficiente para tu bot
- Puedes ver el uso en Dashboard → "Usage"
- Los logs se actualizan en tiempo real
- Cada vez que hagas `git push`, Railway redeployará automáticamente

## 📞 ¿Necesitas ayuda?

Si tienes problemas en algún paso, puedo ayudarte:
- Configurar GitHub
- Debuggear errores de build
- Configurar el webhook
- Revisar logs

