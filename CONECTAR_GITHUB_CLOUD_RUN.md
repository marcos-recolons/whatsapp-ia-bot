# 🔗 Conectar GitHub con Google Cloud Run - Paso a Paso

## 📋 Método 1: Desde Cloud Run Console (Más Fácil)

### Paso 1: Habilitar Cloud Build API

1. Ve a [console.cloud.google.com](https://console.cloud.google.com)
2. Selecciona tu proyecto (o créalo nuevo)
3. Ve a **"APIs & Services"** → **"Library"**
4. Busca **"Cloud Build API"**
5. Click en **"Enable"** (si no está habilitada)

### Paso 2: Conectar GitHub en Cloud Build

1. Ve a [Cloud Build](https://console.cloud.google.com/cloud-build/triggers)
2. Click en **"Connect Repository"** (arriba)
3. Selecciona **"GitHub (Cloud Build GitHub App)"**
4. Click en **"Continue"**
5. Autoriza Google Cloud Build para acceder a GitHub:
   - Te pedirá seleccionar tu cuenta de GitHub
   - Click en **"Authorize google-cloud-build"**
   - Selecciona **"Only select repositories"**
   - Elige: `marcos-recolons/whatsapp-ia-bot`
   - Click en **"Install"**

### Paso 3: Crear Trigger (Automático)

1. Después de conectar, Cloud Build te preguntará si quieres crear un trigger
2. O ve a **"Triggers"** → **"Create Trigger"**
3. Configuración:
   - **Name**: `whatsapp-ia-bot-deploy`
   - **Event**: Push to a branch
   - **Repository**: `marcos-recolons/whatsapp-ia-bot`
   - **Branch**: `^main$`
   - **Configuration**: Dockerfile
   - **Dockerfile location**: `Dockerfile`
   - **Cloud Run region**: `us-central1` (o la más cercana)
   - **Service name**: `whatsapp-ia-bot`
   - Click en **"Create"**

### Paso 4: Desplegar desde Cloud Run (Directo)

**Alternativa más simple** - Desplegar directamente desde Cloud Run:

1. Ve a [Cloud Run](https://console.cloud.google.com/run)
2. Click en **"Create Service"**
3. Selecciona **"Continuously deploy new revisions from a source repository"**
4. Click en **"Set up with Cloud Build"**
5. **Conectar repositorio** (si aún no lo has hecho):
   - Click en **"Connect Repository"**
   - Selecciona **"GitHub (Cloud Build GitHub App)"**
   - Autoriza y selecciona `marcos-recolons/whatsapp-ia-bot`
6. Una vez conectado:
   - **Repository**: Selecciona `marcos-recolons/whatsapp-ia-bot`
   - **Branch**: `main`
   - **Build type**: **Dockerfile**
   - **Dockerfile location**: `Dockerfile` (debería detectarlo automáticamente)
   - Click en **"Next"**

### Paso 5: Configurar el Servicio

1. **Service name**: `whatsapp-ia-bot`
2. **Region**: `us-central1` (o la más cercana a ti)
3. **CPU**: 1 vCPU
4. **Memory**: 512 MiB
5. **Minimum instances**: 0 (para ahorrar)
6. **Maximum instances**: 10
7. Click en **"Next"**

### Paso 6: Variables de Entorno

1. Click en **"Variables & Secrets"** → **"Add Variable"**
2. Agrega cada una:

```
OPENAI_API_KEY = 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
OPENAI_MODEL = gpt-3.5-turbo
WHATSAPP_PROVIDER = meta
WHATSAPP_API_KEY = EAAFyZBW4QBWABPLZB7NKTnl53uU6hn7i4fQdh9ZCZBjrVgUcloQzuE69dtflDkvFpTm8cenKKbBILX86wfoInBZADzc3jle6GJFSdD3CpSAdSEyuMGRJnhdPlQAIhHjlsZCQiDPtuuppcHdzVae0gRxeX8IkRZCZCq95P5vMkOLagDBXyvZAVa46orbQaU1n1wx6skwZDZD
WHATSAPP_PHONE_NUMBER_ID = 378914085314990
WHATSAPP_VERIFY_TOKEN = whatsapp_webhook_verify_token_2024
WHATSAPP_BUSINESS_ACCOUNT_ID = 453485421175530
PORT = 8080
```

3. Click en **"Create"**

### Paso 7: Esperar el Deploy

- Google empezará a construir la imagen Docker
- Luego desplegará en Cloud Run
- Tardará 5-10 minutos
- Verás el progreso en tiempo real

### Paso 8: Obtener tu URL

Una vez completado:
1. Verás tu servicio en Cloud Run
2. URL será algo como: `https://whatsapp-ia-bot-xxxxx-uc.a.run.app`
3. **¡Copia esta URL!** La necesitarás para el webhook

---

## 🔄 Deploy Automático (Después del primer deploy)

Una vez configurado, cada vez que hagas `git push`:
1. Cloud Build detectará el cambio automáticamente
2. Construirá una nueva imagen
3. Desplegará automáticamente en Cloud Run
4. **¡Sin tener que entrar a Google Cloud!**

---

## 🆘 Problemas Comunes

**"Repository not found"**
- Verifica que hayas autorizado el acceso en GitHub
- Ve a GitHub → Settings → Applications → Authorized OAuth Apps
- Verifica que "Google Cloud Build" esté autorizado

**"Permission denied"**
- Verifica que tengas permisos de Editor o Owner en el proyecto de Google Cloud
- Verifica que Cloud Build API esté habilitada

**"Dockerfile not found"**
- Verifica que el Dockerfile esté en la raíz del repositorio
- Verifica que el branch sea `main`

---

## ✅ Verificar que Funciona

Después del deploy:

1. Visita: `https://tu-url.a.run.app/health`
   - Debe responder: `{"status": "healthy", "connected": true}`

2. Revisa los logs:
   - Cloud Run → Tu servicio → "Logs"
   - Deberías ver: "Servidor listo para recibir mensajes"

3. Prueba un push:
   ```bash
   git commit --allow-empty -m "Test deploy"
   git push origin main
   ```
   - Ve a Cloud Build → Verás el build automático
   - Ve a Cloud Run → Verás el nuevo deployment

---

## 📝 Resumen

1. ✅ Conectar GitHub en Cloud Build
2. ✅ Crear servicio en Cloud Run desde GitHub
3. ✅ Configurar variables de entorno
4. ✅ Desplegar
5. ✅ Configurar webhook en Meta con la URL de Cloud Run

¡Listo! Tu bot estará en producción y se actualizará automáticamente con cada `git push`.

