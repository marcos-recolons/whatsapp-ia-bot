# ✅ Solución Final: Error de Puerto

## Cambios Realizados

1. ✅ Dockerfile corregido - Usa `${PORT}` directamente (Cloud Run siempre lo inyecta)
2. ✅ Manejo de errores mejorado
3. ✅ Logging mejorado para diagnóstico

## 🔍 Pasos para Diagnosticar

### 1. Ver los Logs Detallados

**IMPORTANTE**: El mensaje de error que ves es genérico. Necesitamos ver los logs reales:

1. **Opción A - Desde Cloud Run:**
   - Cloud Run → Tu servicio → Pestaña **"Logs"**
   - Busca las últimas líneas con errores

2. **Opción B - Desde Cloud Logging:**
   - Click en **"Abre Cloud Logging"** en el mensaje de error
   - O ve a: https://console.cloud.google.com/logs
   - Filtra por: `resource.labels.service_name="whatsapp-ia-bot"`

### 2. Qué Buscar en los Logs

Busca estas palabras clave:
- `ERROR`
- `Exception`
- `Traceback`
- `Failed`
- `ModuleNotFoundError`
- `ImportError`

### 3. Compartir los Logs

**Copia las últimas 30-50 líneas de los logs** y compártelas para diagnosticar.

## 🚀 Soluciones Rápidas

### Solución 1: Aumentar Timeout

El servidor puede estar tardando mucho en iniciar:

1. Cloud Run → Tu servicio → **Edit & Deploy New Revision**
2. Busca **"Timeouts"** o **"Timeouts"**
3. **Startup timeout**: Cambia a **300 segundos** (5 minutos)
4. **Request timeout**: **300 segundos**
5. Click en **Deploy**

### Solución 2: Verificar Variables de Entorno

Asegúrate de tener estas variables configuradas:

```
OPENAI_API_KEY = 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

WHATSAPP_API_KEY = EAAFyZBW4QBWABPLZB7NKTnl53uU6hn7i4fQdh9ZCZBjrVgUcloQzuE69dtflDkvFpTm8cenKKbBILX86wfoInBZADzc3jle6GJFSdD3CpSAdSEyuMGRJnhdPlQAIhHjlsZCQiDPtuuppcHdzVae0gRxeX8IkRZCZCq95P5vMkOLagDBXyvZAVa46orbQaU1n1wx6skwZDZD

WHATSAPP_PHONE_NUMBER_ID = 378914085314990

WHATSAPP_VERIFY_TOKEN = whatsapp_webhook_verify_token_2024
```

### Solución 3: Probar con Versión Mínima

Si sigue fallando, podemos probar primero con una versión mínima del servidor para verificar que el problema no sea del código complejo.

## ⚠️ Importante

**Sin ver los logs detallados, es difícil diagnosticar el problema exacto.**

El mensaje que ves es genérico y puede tener varias causas:
- Error al instalar dependencias
- Error de importación
- Error de sintaxis
- Timeout (muy común)
- Variables faltantes

**Por favor, comparte los logs detallados para poder ayudarte mejor.**

