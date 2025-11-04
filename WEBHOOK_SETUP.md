# 🔗 Configuración del Webhook en Meta Dashboard

Guía rápida para configurar el webhook una vez que tengas tu servidor desplegado.

## 📋 Información de tu configuración

- **Verify Token**: `whatsapp_webhook_verify_token_2024`
- **Phone Number ID**: `378914085314990`
- **Business Account ID**: `453485421175530`

## 🌐 Pasos para configurar el webhook

### 1. Despliega tu servidor primero

Necesitas tener tu servidor corriendo en una URL HTTPS pública. Ejemplos:
- Railway: `https://tu-app.railway.app`
- Render: `https://tu-app.onrender.com`
- Heroku: `https://tu-app.herokuapp.com`

### 2. Ve a Meta Dashboard

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Selecciona tu App
3. Ve a **WhatsApp** → **Configuration**

### 3. Configurar Webhook

En la sección **Webhook**, haz click en **"Editar"** o **"Configure"**:

1. **Callback URL**: 
   ```
   https://tu-dominio.com/webhook/whatsapp
   ```
   ⚠️ **Importante**: Reemplaza `tu-dominio.com` con tu URL real

2. **Verify Token**: 
   ```
   whatsapp_webhook_verify_token_2024
   ```
   ⚠️ Debe ser **exactamente** igual al que está en tu `.env`

3. Haz click en **"Verificar y guardar"**

   Meta enviará una petición GET a tu servidor. Si todo está bien, verás un ✅ verde.

### 4. Suscribirse a eventos

En la misma página, asegúrate de estar suscrito a:

- ✅ **messages** (mensajes entrantes)
- ✅ **message_status** (opcional, para ver estado de entrega)

### 5. Verificar que funciona

1. Abre WhatsApp en tu teléfono
2. Envía un mensaje al número de WhatsApp Business asociado
3. Revisa los logs de tu servidor - deberías ver:
   ```
   INFO: Webhook recibido: {...}
   INFO: Mensaje recibido de +1234567890: Tu mensaje
   INFO: Respuesta generada para +1234567890
   INFO: Mensaje enviado a +1234567890 via Meta
   ```

## 🔒 Seguridad (Opcional pero recomendado)

Para mayor seguridad, configura el **App Secret** para validar las firmas de los webhooks:

1. En Meta Dashboard → **Configuración** → **Básico**
2. Copia el **App Secret**
3. Agrégalo a tus variables de entorno como `WHATSAPP_APP_SECRET`

## ⚠️ Notas importantes

1. **Access Token temporal**: El token que tienes ahora es temporal (válido ~24 horas). Para producción necesitarás:
   - Configurar un sistema de renovación automática, o
   - Generar un token permanente

2. **Webhook debe ser HTTPS**: Meta solo acepta URLs HTTPS en producción

3. **Verify Token**: Debe coincidir exactamente entre Meta Dashboard y tu servidor

4. **Primer mensaje**: El usuario debe iniciar la conversación primero. No puedes enviar mensajes sin que el usuario haya escrito primero (excepto con plantillas aprobadas).

## 🧪 Probar localmente

Si quieres probar localmente antes de desplegar, puedes usar:

- **ngrok**: `ngrok http 8000` - Te dará una URL HTTPS temporal
- **localtunnel**: `npx localtunnel --port 8000`

Luego usa esa URL temporal en Meta Dashboard para probar.

## 📞 Troubleshooting

**Error: "Webhook verification failed"**
- Verifica que el Verify Token sea exactamente igual
- Asegúrate de que tu servidor esté accesible públicamente
- Revisa los logs de tu servidor

**Error: "Invalid OAuth access token"**
- El token puede haber expirado (son temporales)
- Genera uno nuevo en Meta Dashboard

**Los mensajes no llegan**
- Verifica que el webhook esté verificado (✅ verde)
- Asegúrate de estar suscrito a eventos "messages"
- Revisa los logs de tu servidor

