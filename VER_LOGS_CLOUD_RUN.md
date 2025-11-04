# 📋 Cómo Ver los Logs Detallados en Cloud Run

## 🔍 Paso 1: Acceder a los Logs

1. Ve a [Cloud Run Console](https://console.cloud.google.com/run)
2. Click en tu servicio: **whatsapp-ia-bot**
3. En la parte superior, verás varias pestañas
4. Click en la pestaña **"Logs"** o **"Registros"**

## 🔍 Paso 2: Ver Logs del Último Deploy

1. En la página de Logs, busca el filtro o dropdown
2. Selecciona la **revisión más reciente** (la que falló)
3. O busca por timestamp del último deploy

## 🔍 Paso 3: Buscar Errores

En los logs, busca:
- Mensajes en **rojo** o con "ERROR"
- Palabras clave: `Error`, `Exception`, `Failed`, `Traceback`
- Al final de los logs (últimas líneas)

## 📸 Qué Compartir

**Copia y pega aquí:**
1. Las últimas 20-30 líneas de los logs
2. Cualquier mensaje de error que veas
3. Mensajes que empiecen con "ERROR" o "Exception"

## 🔗 Alternativa: Cloud Logging Directo

Si no encuentras los logs en Cloud Run:

1. Ve a [Cloud Logging](https://console.cloud.google.com/logs)
2. En el filtro, escribe:
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name="whatsapp-ia-bot"
   ```
3. Ordena por tiempo (más reciente primero)
4. Busca errores

## 💡 Qué Buscar Específicamente

Los errores más comunes son:

**Si ves esto:**
```
ModuleNotFoundError: No module named 'fastapi'
```
→ Problema con requirements.txt

**Si ves esto:**
```
ImportError: cannot import name 'X'
```
→ Problema con imports en el código

**Si ves esto:**
```
SyntaxError: invalid syntax
```
→ Error de sintaxis en Python

**Si ves esto:**
```
Address already in use
```
→ Problema con el puerto

**Si NO ves ningún error:**
→ El servidor puede estar iniciando pero muy lento
→ Aumenta el timeout a 300 segundos

---

## 🚨 Si No Puedes Ver los Logs

Comparte una captura de pantalla de:
- La página de Cloud Run → Tu servicio
- La pestaña de Logs (aunque esté vacía)
- Cualquier mensaje que veas

