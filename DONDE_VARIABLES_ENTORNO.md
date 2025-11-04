# 🔍 Dónde Configurar Variables de Entorno en Cloud Run

## 📍 Ubicación de las Variables de Entorno

Las variables de entorno están en la **configuración de la revisión** del servicio.

### Método 1: Desde la Pestaña "Revisiones" (Revisions)

1. **Ve a la pestaña "Revisiones"** (al lado de "Seguridad")
2. Verás una lista de revisiones del servicio
3. Click en la **revisión más reciente** (o la única que haya)
4. Busca la sección **"Variables y secretos"** o **"Variables & Secrets"**
5. Click en **"Edit & Deploy New Revision"** o **"Editar y desplegar nueva revisión"**
6. Ahí podrás agregar las variables

### Método 2: Desde la Configuración del Contenedor

1. En la misma página del servicio (pestaña "Revisiones")
2. Haz click en **"Edit & Deploy New Revision"**
3. Desplázate hacia abajo hasta **"Contenedores, volúmenes, redes y seguridad"**
4. Expande esa sección
5. Busca **"Variables y secretos"** o **"Variables & Secrets"**
6. Click en **"Add Variable"** o **"Agregar variable"**

### Método 3: Desde el Editor YAML

1. Ve a la pestaña **"YAML"** (al final de las pestañas)
2. Ahí verás la configuración completa
3. Busca la sección `env:` o `envVars:`
4. Puedes editarlo directamente, pero es más complejo

---

## ✅ Pasos Recomendados (Más Fácil)

1. **Click en la pestaña "Revisiones"** (Revisions)
2. **Click en "Edit & Deploy New Revision"** o el botón de editar
3. **Desplázate hacia abajo** hasta encontrar:
   - **"Variables y secretos"** o
   - **"Variables & Secrets"** o
   - **"Environment variables"**
4. **Click en "Add Variable"** o **"Agregar variable"**
5. Agrega cada variable una por una

---

## 📝 Variables que Necesitas Agregar

Cuando encuentres la sección, agrega estas variables:

```
OPENAI_API_KEY = tu_openai_api_key_aqui

OPENAI_MODEL = gpt-3.5-turbo

WHATSAPP_PROVIDER = meta

WHATSAPP_API_KEY = tu_whatsapp_access_token_aqui

WHATSAPP_PHONE_NUMBER_ID = 378914085314990

WHATSAPP_VERIFY_TOKEN = whatsapp_webhook_verify_token_2024

WHATSAPP_BUSINESS_ACCOUNT_ID = 453485421175530

PORT = 8080
```

---

## 🎯 Tu URL del Servicio

**Tu servicio ya está desplegado:**
```
https://whatsapp-ia-bot-74824094374.europe-southwest1.run.app
```

**URL para el webhook de Meta:**
```
https://whatsapp-ia-bot-74824094374.europe-southwest1.run.app/webhook/whatsapp
```

---

## 🔍 Si No Encuentras las Variables

1. **Prueba hacer scroll hacia abajo** en la página de edición
2. **Busca secciones colapsables** - haz click para expandirlas
3. **Mira todas las pestañas** - puede estar en "Configuración" o "Container"
4. **Usa Ctrl+F (Cmd+F en Mac)** y busca "variable" o "env"

---

## 💡 Alternativa: Configurar desde Terminal

Si no encuentras la opción en la interfaz, puedo ayudarte a configurarlas desde la terminal usando `gcloud`.

