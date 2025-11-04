# 🔧 Fix Definitivo: Error de Puerto en Cloud Run

## Cambios Realizados

1. ✅ Manejo de errores mejorado - El servidor inicia incluso sin todas las variables
2. ✅ Dockerfile mejorado - Uso explícito de PORT
3. ✅ Logging mejorado - Para diagnosticar problemas

## ⚠️ IMPORTANTE: Verificar Logs

El error puede tener varias causas. **Primero revisa los logs:**

1. Ve a Cloud Run → Tu servicio → Pestaña **"Logs"**
2. Busca los últimos logs del despliegue
3. **Compárteme qué error ves** - puede ser:
   - Error de importación
   - Error al instalar dependencias
   - Error de sintaxis
   - Variables faltantes

## ✅ Configuración Necesaria

Asegúrate de tener estas variables configuradas:

```
OPENAI_API_KEY = tu_openai_api_key_aqui

WHATSAPP_API_KEY = tu_whatsapp_access_token_aqui

WHATSAPP_PHONE_NUMBER_ID = 378914085314990

WHATSAPP_VERIFY_TOKEN = whatsapp_webhook_verify_token_2024
```

## 🔍 Diagnóstico Rápido

**Si los logs muestran:**

- `ModuleNotFoundError` → Falta dependencia en requirements.txt
- `ImportError` → Problema con imports
- `SyntaxError` → Error de sintaxis en el código
- `AttributeError` → Variable no inicializada correctamente
- `Timeout` → El servidor tarda mucho en iniciar

## 💡 Solución Alternativa: Aumentar Timeout

Si el problema es solo tiempo:

1. Cloud Run → Tu servicio → Edit
2. Busca **"Timeouts"**
3. **Startup timeout**: 300 segundos (5 minutos)
4. **Request timeout**: 300 segundos

## 🚀 Próximos Pasos

1. **Revisa los logs** y compárteme el error exacto
2. **Verifica las variables** están configuradas
3. **Intenta desplegar de nuevo** con los cambios actualizados

