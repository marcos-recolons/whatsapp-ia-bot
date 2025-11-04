# ☁️ Despliegue en Google Cloud Platform

Guía completa para desplegar tu bot de WhatsApp en Google Cloud Run (serverless, paga solo por uso).

## 🎯 Ventajas de Google Cloud Run

- ✅ **Serverless** - No gestionas servidores
- ✅ **Escala automáticamente** - De 0 a millones de requests
- ✅ **Paga solo por uso** - Muy económico
- ✅ **HTTPS incluido** - Certificado SSL automático
- ✅ **Deploy automático** - Cada push a GitHub puede desplegar automáticamente
- ✅ **Siempre activo** - Sin "sleep" como Render

## 💰 Costos

### Plan Free de Google Cloud
- **$300 de crédito gratis** durante 90 días para nuevos usuarios
- Después: solo pagas por lo que uses

### Cloud Run Pricing
- **Gratis**: Primeros 2 millones de requests/mes
- **CPU**: $0.00002400 por segundo (muy barato)
- **Memoria**: $0.00000250 por GB-segundo
- **Estimado para tu bot**: **$0-5/mes** (probablemente gratis con el tier free)

## 📋 Requisitos Previos

1. **Cuenta de Google Cloud**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Google Cloud SDK** instalado (opcional, puedes usar la consola web)
3. **Tu código en GitHub** (ya lo tienes: https://github.com/marcos-recolons/whatsapp-ia-bot)

## 🚀 Opción 1: Cloud Run (Recomendado - Más Fácil)

### Paso 1: Crear proyecto en Google Cloud

1. Ve a [console.cloud.google.com](https://console.cloud.google.com)
2. Click en el selector de proyectos (arriba) → **"New Project"**
3. Nombre: `whatsapp-ia-bot`
4. Click en **"Create"**
5. Espera a que se cree el proyecto

### Paso 2: Habilitar APIs necesarias

1. En el menú lateral → **"APIs & Services"** → **"Library"**
2. Busca y habilita:
   - **Cloud Run API**
   - **Cloud Build API**
   - **Container Registry API**

### Paso 3: Subir código a GitHub

**Si aún no lo has hecho**, ejecuta:

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer
git add .
git commit -m "Add Dockerfile for Google Cloud"
git push origin main
```

### Paso 4: Desplegar desde GitHub (Método Fácil)

#### Opción A: Desde la Consola Web

1. Ve a [Cloud Run](https://console.cloud.google.com/run)
2. Click en **"Create Service"**
3. **"Deploy one revision from an existing container image"** o **"Continuously deploy new revisions from a source repository"**
4. Si eliges GitHub:
   - Conecta tu repositorio
   - Selecciona: `marcos-recolons/whatsapp-ia-bot`
   - Build type: **Dockerfile**
   - Service name: `whatsapp-ia-bot`
   - Region: `us-central1` (o la más cercana)
   - Click en **"Next"**

5. **Configurar variables de entorno:**
   - Click en **"Variables & Secrets"**
   - Agrega cada variable:
     ```
     OPENAI_API_KEY=tu_openai_api_key_aqui
     OPENAI_MODEL=gpt-3.5-turbo
     WHATSAPP_PROVIDER=meta
     WHATSAPP_API_KEY=tu_whatsapp_access_token_aqui
     WHATSAPP_PHONE_NUMBER_ID=378914085314990
     WHATSAPP_VERIFY_TOKEN=whatsapp_webhook_verify_token_2024
     WHATSAPP_BUSINESS_ACCOUNT_ID=453485421175530
     PORT=8080
     ```

6. **Configuración del servicio:**
   - CPU: 1 vCPU
   - Memory: 512 MiB (suficiente)
   - Min instances: 0 (para ahorrar)
   - Max instances: 10
   - Click en **"Create"**

7. **Espera 5-10 minutos** mientras Google construye y despliega

8. **Obtén tu URL:**
   - Una vez desplegado, verás una URL como: `https://whatsapp-ia-bot-xxxxx-uc.a.run.app`
   - Esta es tu URL pública ✅

### Paso 5: Configurar Webhook en Meta

1. Ve a Meta Dashboard → WhatsApp → Configuration
2. Webhook URL: `https://tu-url-de-cloud-run.a.run.app/webhook/whatsapp`
3. Verify Token: `whatsapp_webhook_verify_token_2024`
4. Click en **"Verify and Save"**
5. Suscríbete a eventos: ✅ **messages**

### Paso 6: Configurar Deploy Automático (Opcional)

Para que cada `git push` despliegue automáticamente:

1. En Cloud Run → Tu servicio → **"Continuous deployment"**
2. Conecta tu repositorio de GitHub
3. Configura el trigger
4. ¡Listo! Cada push desplegará automáticamente

---

## 🚀 Opción 2: Desde Terminal (Más Control)

### Instalar Google Cloud SDK

```bash
# macOS
brew install --cask google-cloud-sdk

# O descarga desde: https://cloud.google.com/sdk/docs/install
```

### Autenticarse

```bash
gcloud auth login
gcloud config set project whatsapp-ia-bot
```

### Construir y desplegar

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer

# Construir imagen
gcloud builds submit --tag gcr.io/$PROJECT_ID/whatsapp-ia-bot

# Desplegar en Cloud Run
gcloud run deploy whatsapp-ia-bot \
  --image gcr.io/$PROJECT_ID/whatsapp-ia-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="tu_openai_api_key_aqui",OPENAI_MODEL="gpt-3.5-turbo",WHATSAPP_PROVIDER="meta",WHATSAPP_API_KEY="tu_whatsapp_access_token_aqui",WHATSAPP_PHONE_NUMBER_ID="tu_phone_number_id",WHATSAPP_VERIFY_TOKEN="tu_verify_token",WHATSAPP_BUSINESS_ACCOUNT_ID="tu_business_account_id",PORT="8080"
```

**Nota**: Es mejor configurar las variables desde la consola web para evitar problemas con caracteres especiales.

---

## 🚀 Opción 3: Compute Engine (VPS Tradicional)

Si prefieres un servidor tradicional (más control, pero más mantenimiento):

1. Ve a [Compute Engine](https://console.cloud.google.com/compute)
2. Click en **"Create Instance"**
3. Configuración:
   - Machine type: `e2-micro` (gratis siempre)
   - Boot disk: Ubuntu 22.04
   - Firewall: Allow HTTP y HTTPS
4. Click en **"Create"**
5. Conecta por SSH y configura manualmente

**Costos**: Gratis con tier free, después ~$5-10/mes

---

## ✅ Verificar que Funciona

1. Visita: `https://tu-url.a.run.app/health`
   - Debe responder: `{"status": "healthy", "connected": true}`

2. Prueba el webhook:
```bash
curl https://tu-url.a.run.app/webhook/whatsapp/send?to=+34627191450&message=Hola
```

3. Envía un mensaje desde WhatsApp al número +34 627 19 14 50

---

## 🔄 Actualizar el Bot

### Si configuraste deploy automático:
- Solo haz `git push` y se actualizará automáticamente

### Manualmente:
```bash
# Hacer cambios
git add .
git commit -m "Update bot"
git push origin main

# En Cloud Run console, click en "Deploy new revision"
# O desde terminal:
gcloud run deploy whatsapp-ia-bot --source .
```

---

## 💡 Ventajas vs Railway

- ✅ **Más control** - Puedes elegir región, recursos, etc.
- ✅ **Mejor para producción** - Escalabilidad empresarial
- ✅ **Integración con otros servicios Google** - Cloud Storage, BigQuery, etc.
- ✅ **Siempre activo** - Sin límites de tiempo
- ✅ **Deploy automático desde GitHub** - Configurable

---

## 🆘 Troubleshooting

**Error: "Permission denied"**
- Verifica que hayas habilitado las APIs necesarias
- Verifica que tengas permisos de Editor o Owner

**Error: "Build failed"**
- Revisa que el Dockerfile esté correcto
- Verifica los logs en Cloud Build

**El servicio no responde**
- Verifica que las variables de entorno estén configuradas
- Revisa los logs en Cloud Run → Logs

**Costo inesperado**
- Revisa el uso en Billing Dashboard
- Configura alertas de presupuesto

---

## 📚 Recursos

- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Free Tier](https://cloud.google.com/free)

