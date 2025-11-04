# 🔥 Configuración de Firestore

Este sistema utiliza Google Cloud Firestore para almacenar los datos de los usuarios.

## ⚡ Configuración Rápida desde Consola (Recomendado)

La forma más simple es usar `gcloud` desde la consola:

### 1. Instalar Google Cloud SDK (si no lo tienes)

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Windows
# Descarga desde https://cloud.google.com/sdk/docs/install
```

### 2. Autenticarse

```bash
gcloud auth login
gcloud auth application-default login
```

El segundo comando configura las credenciales por defecto que usará la aplicación.

### 3. Configurar el Proyecto

```bash
# Listar proyectos disponibles
gcloud projects list

# Configurar el proyecto que quieres usar
gcloud config set project TU_PROJECT_ID
```

### 4. Habilitar Firestore

```bash
# Habilitar la API de Firestore
gcloud services enable firestore.googleapis.com

# Crear base de datos Firestore (si no existe)
# Ve a https://console.cloud.google.com/firestore y crea una base de datos
# O usa el comando:
gcloud firestore databases create --region=us-central
```

### 5. Configurar Variable de Entorno (Opcional)

Si quieres especificar el proyecto explícitamente:

```bash
export GOOGLE_CLOUD_PROJECT=TU_PROJECT_ID
```

O en tu archivo `.env`:
```
GOOGLE_CLOUD_PROJECT=tu-proyecto-id
```

¡Eso es todo! El sistema detectará automáticamente las credenciales configuradas con `gcloud auth application-default login`.

---

## 🔧 Otras Opciones de Configuración

### Opción A: Variable de Entorno con JSON (Para Cloud Run / Railway)

Si prefieres usar credenciales de cuenta de servicio:

1. Crea una cuenta de servicio en Google Cloud Console
2. Descarga el JSON de credenciales
3. Configura la variable de entorno:

```bash
FIRESTORE_CREDENTIALS='{"type":"service_account","project_id":"tu-proyecto",...}'
```

### Opción B: Archivo de Credenciales

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/ruta/a/tu/credenciales.json
```

### Opción C: Credenciales por Defecto (Cloud Run / GCP)

Si estás ejecutando en Google Cloud Run o Compute Engine, las credenciales se detectan automáticamente.

---

## 📊 Estructura de la Base de Datos

Firestore organizará los datos así:

```
users/
  └── {phone_number}/
      ├── name: string
      ├── interests: string
      ├── created_at: timestamp
      ├── updated_at: timestamp
      ├── onboarding_completed: boolean
      ├── last_challenge_date: timestamp (nullable)
      └── challenges_completed: number
```

## 🔐 Permisos Necesarios

Para desarrollo local con `gcloud auth application-default login`, tu cuenta de usuario necesita estos permisos en el proyecto:
- `datastore.entities.create`
- `datastore.entities.get`
- `datastore.entities.update`

O simplemente el rol: **Cloud Datastore User** o **Firestore User**

## ✅ Verificación

Cuando inicies el servidor, verás en los logs:
```
Firestore inicializado con credenciales por defecto (proyecto: tu-proyecto-id)
Firestore conectado: Sí
```

Si ves un error, verifica:
1. Que hayas ejecutado `gcloud auth application-default login`
2. Que hayas configurado el proyecto con `gcloud config set project`
3. Que Firestore esté habilitado en el proyecto

## 🆘 Troubleshooting

**Error: "No se pudieron inicializar las credenciales"**
- Ejecuta: `gcloud auth application-default login`
- Verifica: `gcloud config get-value project`

**Error: "Permission denied"**
- Verifica que tu cuenta tenga permisos en el proyecto
- En Google Cloud Console → IAM & Admin → IAM, verifica tus permisos

**Error: "Database not found"**
- Asegúrate de haber creado la base de datos Firestore
- Ve a https://console.cloud.google.com/firestore y crea una base de datos

**Error: "Project not found"**
- Verifica el proyecto: `gcloud config get-value project`
- O configura: `export GOOGLE_CLOUD_PROJECT=tu-proyecto-id`
