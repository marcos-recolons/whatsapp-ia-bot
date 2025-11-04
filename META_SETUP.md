# 📱 Configuración de Meta WhatsApp Business API

Guía completa para configurar la API oficial de WhatsApp Business de Meta.

## 📋 Requisitos Previos

1. **Cuenta de Meta Business**: [business.facebook.com](https://business.facebook.com)
2. **App de Meta**: Creada en [developers.facebook.com](https://developers.facebook.com)
3. **Número de teléfono verificado** para WhatsApp Business
4. **Tu servidor desplegado** con URL HTTPS pública

## 🔧 Paso 1: Crear App en Meta

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Click en "Mis Apps" → "Crear App"
3. Selecciona "Empresa" como tipo de app
4. Completa la información básica
5. En el Dashboard, busca "WhatsApp" y haz click en "Configurar"

## 🔑 Paso 2: Obtener Credenciales

### Access Token (WHATSAPP_API_KEY)

1. En el Dashboard de tu App → "WhatsApp" → "Getting Started"
2. Copia el **Temporary Access Token** (válido por 24 horas)
3. Para producción, necesitas un **Permanent Access Token**:
   - Ve a "WhatsApp" → "API Setup"
   - Click en "Generate Token" (requiere permisos de administrador)
   - O configura un sistema de renovación automática

### Phone Number ID (WHATSAPP_PHONE_NUMBER_ID)

1. En "WhatsApp" → "Getting Started"
2. Busca **"Phone number ID"**
3. Copia el ID (es un número largo)

### App Secret (WHATSAPP_APP_SECRET) - Opcional pero recomendado

1. En el Dashboard → "Configuración" → "Básico"
2. Busca "App Secret"
3. Click en "Mostrar" y copia el secreto
4. **Importante**: Úsalo para verificar la firma de los webhooks

### Verify Token (WHATSAPP_VERIFY_TOKEN)

1. **Crea tu propio token** (puede ser cualquier string aleatorio)
2. Ejemplo: `mi_token_secreto_12345`
3. Este token lo usarás para verificar el webhook

## 🌐 Paso 3: Configurar Webhook

### 3.1 En tu servidor (ya está configurado)

Tu servidor ya tiene los endpoints necesarios:
- `GET /webhook/whatsapp` - Para verificación
- `POST /webhook/whatsapp` - Para recibir mensajes

### 3.2 En Meta Dashboard

1. Ve a "WhatsApp" → "Configuration"
2. En "Webhook", click en "Editar"
3. **Callback URL**: `https://tu-dominio.com/webhook/whatsapp`
4. **Verify Token**: El mismo que configuraste en `WHATSAPP_VERIFY_TOKEN`
5. Click en "Verificar y guardar"

Meta enviará una petición GET a tu servidor para verificar que eres el dueño.

### 3.3 Suscribirse a eventos

En la misma página de configuración:
- Marca: ✅ **messages**
- Marca: ✅ **message_status** (opcional, para ver estado de entrega)

## 🔐 Paso 4: Configurar Variables de Entorno

En tu servidor (Railway, Render, etc.) o en `.env` local:

```bash
# WhatsApp Meta API
WHATSAPP_PROVIDER=meta
WHATSAPP_API_KEY=tu_access_token_aqui
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id_aqui
WHATSAPP_VERIFY_TOKEN=tu_token_secreto_aqui
WHATSAPP_APP_SECRET=tu_app_secret_aqui  # Opcional pero recomendado

# OpenAI (ya configurado)
OPENAI_API_KEY=tu_openai_key
OPENAI_MODEL=gpt-3.5-turbo
```

## ✅ Paso 5: Verificar que Funciona

### 5.1 Verificar webhook

1. En Meta Dashboard → "WhatsApp" → "Configuration"
2. Deberías ver un ✅ verde junto a "Webhook"
3. Si hay un error, revisa los logs de tu servidor

### 5.2 Enviar mensaje de prueba

1. Abre WhatsApp en tu teléfono
2. Envía un mensaje al número de WhatsApp Business
3. Revisa los logs de tu servidor:
   ```bash
   # Deberías ver:
   INFO: Webhook recibido: {...}
   INFO: Mensaje recibido de +1234567890: Hola
   INFO: Respuesta generada para +1234567890
   INFO: Mensaje enviado a +1234567890 via Meta (ID: ...)
   ```

### 5.3 Probar endpoint de envío manual

```bash
curl -X POST "https://tu-dominio.com/webhook/whatsapp/send?to=+1234567890&message=Hola%20desde%20API"
```

## 🚨 Solución de Problemas

### Error: "Webhook verification failed"

- Verifica que `WHATSAPP_VERIFY_TOKEN` sea exactamente el mismo en Meta y en tu servidor
- Asegúrate de que tu servidor esté accesible públicamente (HTTPS)
- Revisa los logs del servidor para ver qué token recibió

### Error: "Invalid OAuth access token"

- El Access Token temporal expira en 24 horas
- Genera uno nuevo o configura un sistema de renovación
- Para producción, usa un Access Token permanente

### Error: "Invalid phone number ID"

- Verifica que `WHATSAPP_PHONE_NUMBER_ID` sea correcto
- Debe ser el ID del número que aparece en Meta Dashboard

### Error: "Message failed to send"

- Verifica que el número destino tenga el formato correcto (sin +)
- Asegúrate de que el número haya iniciado una conversación contigo primero
- Revisa los permisos de tu App en Meta

### Los mensajes no llegan al servidor

- Verifica que el webhook esté configurado y verificado en Meta
- Revisa que estés suscrito a los eventos "messages"
- Asegúrate de que tu servidor responda con 200 OK

## 📚 Recursos Adicionales

- [Documentación oficial de Meta WhatsApp API](https://developers.facebook.com/docs/whatsapp)
- [Guía de webhooks de Meta](https://developers.facebook.com/docs/graph-api/webhooks)
- [API Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/reference)

## 🔒 Seguridad

1. **Nunca compartas** tu Access Token públicamente
2. **Usa HTTPS** siempre en producción
3. **Verifica las firmas** de los webhooks usando `WHATSAPP_APP_SECRET`
4. **Rota los tokens** regularmente
5. **Usa variables de entorno** nunca hardcodees credenciales

## 💡 Tips

- El Access Token temporal es útil para desarrollo y pruebas
- Para producción, considera usar un sistema de renovación automática
- Los mensajes tienen una ventana de 24 horas para responder sin costo
- Después de 24 horas, necesitas usar una plantilla aprobada

