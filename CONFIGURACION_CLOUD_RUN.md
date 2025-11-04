# ⚙️ Configuración de Cloud Run - Opciones Recomendadas

## ✅ Configuración Actual (Correcta)

Basándome en tu pantalla:

### 1. Repositorio de Origen ✅
- **Repositorio**: `marcos-recolons/whatsapp-ia-bot` ✅ Correcto
- Cloud Build Trigger se creará automáticamente ✅

### 2. Configurar ✅
- **Nombre de Servicio**: `whatsapp-ia-bot` ✅ Correcto
- **Región**: `europe-west1 (Bélgica)` ✅ Perfecto para Europa
- **URL**: `https://whatsapp-ia-bot-74824094374.europe-west1.run.app` ✅

### 3. Autenticación ✅
- **Permite el acceso público** ✅ **CORRECTO** - Necesario para webhooks de Meta

### 4. Facturación ✅
- **Basada en solicitudes** ✅ **CORRECTO** - Más económico, solo pagas cuando hay tráfico

### 5. Escalamiento de Servicios ✅
- **Ajuste de escala automático** ✅ Correcto
- **Número mínimo de instancias**: `0` ✅ **PERFECTO** - Ahorra dinero
- **Número máximo de instancias**: Deja vacío o pon `10` (suficiente)

### 6. Ingress ✅
- **Todos** ✅ **CORRECTO** - Permite acceso desde Internet (necesario para webhooks)

---

## 🔧 Configuración Adicional Necesaria

### Paso 1: Desplegar Variables de Entorno

**IMPORTANTE**: Necesitas hacer scroll hacia abajo o expandir la sección:
**"Contenedores, volúmenes, redes y seguridad"**

1. Click en esa sección para expandirla
2. Busca **"Variables y secretos"** o **"Variables & Secrets"**
3. Click en **"Add Variable"** o **"Agregar variable"**
4. Agrega cada una de estas variables:

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

### Paso 2: Configuración de Contenedor (Opcional pero Recomendado)

En la misma sección "Contenedores, volúmenes, redes y seguridad":

- **CPU**: 1 vCPU (suficiente)
- **Memoria**: 512 MiB (suficiente para tu bot)
- **Timeout**: 300 segundos (5 minutos) - suficiente
- **Concurrencia**: 80 (por defecto está bien)

---

## ✅ Resumen de Configuración Óptima

| Opción | Valor Recomendado | ¿Por qué? |
|--------|-------------------|-----------|
| **Autenticación** | Acceso público | Webhooks de Meta necesitan acceso público |
| **Facturación** | Basada en solicitudes | Más económico, solo pagas cuando hay tráfico |
| **Mínimo instancias** | 0 | Ahorra dinero, se escala cuando hay mensajes |
| **Máximo instancias** | 10 | Suficiente para un bot de WhatsApp |
| **Ingress** | Todos | Necesario para webhooks |
| **Región** | europe-west1 | Cercana a España, buena latencia |
| **CPU** | 1 vCPU | Suficiente para procesar mensajes |
| **Memoria** | 512 MiB | Suficiente para el bot |

---

## 🚀 Siguiente Paso

Una vez configuradas las variables de entorno:

1. **Click en "Create"** o **"Crear"** (abajo de la página)
2. **Espera 5-10 minutos** mientras Google:
   - Construye la imagen Docker
   - Despliega el servicio
3. **Obtén tu URL**: Ya la tienes: `https://whatsapp-ia-bot-74824094374.europe-west1.run.app`
4. **Configura el webhook en Meta** con esa URL

---

## 🔍 Verificar Después del Deploy

1. Visita: `https://whatsapp-ia-bot-74824094374.europe-west1.run.app/health`
   - Debe responder: `{"status": "healthy", "connected": true}`

2. Revisa los logs:
   - Cloud Run → Tu servicio → Pestaña "Logs"
   - Deberías ver: "Servidor listo para recibir mensajes"

---

## ⚠️ Notas Importantes

- **Cold Start**: Con mínimo 0 instancias, el primer mensaje puede tardar ~10-30 segundos
- Si necesitas respuesta instantánea, cambia mínimo a 1 (costará más)
- La URL puede cambiar después del primer deploy - verifica en la página del servicio

---

## 📝 Tu URL Actual

**Guarda esta URL para el webhook de Meta:**
```
https://whatsapp-ia-bot-74824094374.europe-west1.run.app/webhook/whatsapp
```

