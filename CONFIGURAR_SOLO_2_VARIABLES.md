# 🔐 Configurar Solo las 2 Variables Sensibles

## Desde la Interfaz Web

### Paso 1: Ir a Revisiones
1. Click en la pestaña **"Revisiones"** (Revisions)
2. Verás una revisión del servicio

### Paso 2: Editar Revisión
1. Click en **"Edit & Deploy New Revision"** o el botón de editar (lápiz)
2. Desplázate hacia abajo hasta encontrar **"Variables y secretos"** o **"Variables & Secrets"**

### Paso 3: Agregar Solo las 2 Variables

Click en **"Add Variable"** o **"Agregar variable"** y agrega solo estas dos:

**Variable 1:**
- **Name**: `OPENAI_API_KEY`
- **Value**: `tu_openai_api_key_aqui`

**Variable 2:**
- **Name**: `WHATSAPP_API_KEY`
- **Value**: `tu_whatsapp_access_token_aqui`

### Paso 4: Guardar
1. Click en **"Deploy"** o **"Desplegar"**
2. Espera 2-3 minutos mientras se despliega la nueva revisión

---

## ⚠️ Nota sobre las Otras Variables

Las demás variables tienen valores por defecto en el código, pero para que funcione completamente necesitarás estas también (aunque no son tan sensibles):

- `WHATSAPP_PHONE_NUMBER_ID` (puedes agregarla después si no funciona)
- `WHATSAPP_VERIFY_TOKEN` (necesaria para el webhook)
- `WHATSAPP_PROVIDER=meta` (por defecto ya está configurado como "meta")
- `PORT=8080` (Cloud Run lo inyecta automáticamente)

**Por ahora, prueba con solo las 2 variables sensibles y veamos si funciona.**

---

## ✅ Después de Configurar

1. Visita: `https://whatsapp-ia-bot-74824094374.europe-southwest1.run.app/health`
   - Debe responder: `{"status": "healthy", "connected": true}`

2. Si ves errores en los logs, entonces necesitaremos agregar las otras variables.

3. Configura el webhook en Meta con:
   - URL: `https://whatsapp-ia-bot-74824094374.europe-southwest1.run.app/webhook/whatsapp`
   - Verify Token: `whatsapp_webhook_verify_token_2024`

