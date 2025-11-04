# 🔧 Solución: Subir Código a GitHub

## Problema
Estás autenticado como `MarcosRLP` pero el repositorio es de `marcos-recolons`.

## ✅ Solución Rápida

### Opción 1: Cambiar a la cuenta correcta (Recomendado)

```bash
# Cerrar sesión actual
gh auth logout

# Iniciar sesión con la cuenta correcta
gh auth login
```

Cuando te pregunte:
- **Account**: Selecciona `marcos-recolons` o inicia sesión con esa cuenta
- **Protocol**: HTTPS
- **Git credential**: GitHub CLI

Luego:
```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer
git push origin main
```

### Opción 2: Usar Personal Access Token

Si prefieres mantener tu cuenta actual:

1. Ve a GitHub → Settings → Developer settings → Personal access tokens
2. Crea un token con permisos `repo`
3. Usa el token como contraseña:

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer
git push origin main
```

Cuando pida credenciales:
- Username: `marcos-recolons`
- Password: (pega el token)

### Opción 3: Agregar colaborador

Si quieres mantener ambas cuentas:
1. Ve a https://github.com/marcos-recolons/whatsapp-ia-bot/settings/access
2. Agrega `MarcosRLP` como colaborador
3. Luego podrás hacer push

---

## 🚀 Una vez subido

El código estará en: https://github.com/marcos-recolons/whatsapp-ia-bot

Y podrás continuar con el despliegue en Google Cloud Run.

