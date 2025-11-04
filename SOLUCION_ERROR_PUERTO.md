# 🔧 Solución: Error de Puerto en Cloud Run

## Problema
El contenedor no está escuchando en el puerto 8080 dentro del timeout.

## ✅ Soluciones

### Solución 1: Verificar Variables de Entorno

El problema puede ser que faltan variables y el código falla antes de iniciar.

**Agrega estas variables en Cloud Run:**

1. Ve a Cloud Run → Tu servicio → "Edit & Deploy New Revision"
2. Variables & Secrets → Agrega:

```
OPENAI_API_KEY = tu_openai_api_key_aqui

WHATSAPP_API_KEY = tu_whatsapp_access_token_aqui

WHATSAPP_PHONE_NUMBER_ID = 378914085314990

WHATSAPP_VERIFY_TOKEN = whatsapp_webhook_verify_token_2024
```

### Solución 2: Aumentar Timeout

1. En la configuración del servicio, busca **"Timeouts"**
2. **Startup timeout**: Aumenta a 300 segundos (5 minutos)
3. **Request timeout**: 300 segundos

### Solución 3: Verificar Logs

1. Ve a Cloud Run → Tu servicio → Pestaña **"Logs"**
2. Revisa los últimos logs para ver qué error está ocurriendo
3. Busca mensajes como:
   - "Error starting"
   - "Failed to"
   - "Exception"

### Solución 4: Probar Localmente Primero

Para verificar que el código funciona:

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer

# Crear archivo .env con las variables
cat > .env << EOF
OPENAI_API_KEY=tu_openai_api_key_aqui
WHATSAPP_API_KEY=tu_whatsapp_access_token_aqui
WHATSAPP_PHONE_NUMBER_ID=378914085314990
WHATSAPP_VERIFY_TOKEN=whatsapp_webhook_verify_token_2024
PORT=8080
EOF

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

Si funciona localmente en el puerto 8080, entonces el problema es de configuración en Cloud Run.

---

## 🔍 Diagnóstico

**¿Qué revisar en los logs de Cloud Run?**

1. ¿El contenedor se está construyendo correctamente?
2. ¿Hay errores al instalar dependencias?
3. ¿El servidor está intentando iniciar?
4. ¿Hay errores de importación de módulos?

---

## 💡 Solución Rápida

**Lo más probable es que falten variables de entorno.**

Agrega las 4 variables mencionadas arriba y vuelve a desplegar.

Si aún no funciona, comparte los logs de Cloud Run y te ayudo a diagnosticar.

