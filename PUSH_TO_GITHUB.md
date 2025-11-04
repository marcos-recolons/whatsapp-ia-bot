# 📤 Subir Código a GitHub

## Método 1: Personal Access Token (Recomendado)

### Paso 1: Crear Token en GitHub

1. Ve a GitHub → Click en tu avatar (arriba derecha) → **Settings**
2. En el menú lateral → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. Click en **"Generate new token"** → **"Generate new token (classic)"**
5. Nombre: `whatsapp-bot-deploy`
6. Selecciona permisos:
   - ✅ **repo** (acceso completo a repositorios)
7. Click en **"Generate token"**
8. **¡COPIA EL TOKEN INMEDIATAMENTE!** (solo se muestra una vez)

### Paso 2: Subir código

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer

# Usar el token como contraseña cuando git pida credenciales
git push origin main
```

Cuando te pida:
- **Username**: `marcos-recolons`
- **Password**: Pega el token que copiaste

---

## Método 2: GitHub CLI (Más Fácil)

### Instalar GitHub CLI

```bash
brew install gh
```

### Autenticarse

```bash
gh auth login
```

Sigue las instrucciones (abrirá el navegador para autorizar).

### Subir código

```bash
cd /Users/marcosrecolons/Desktop/Proyectos/MindExplorer
git push origin main
```

---

## Método 3: Desde GitHub Web (Alternativa)

Si prefieres, puedes:
1. Comprimir la carpeta del proyecto
2. Subir los archivos manualmente desde GitHub web
3. O usar GitHub Desktop app

---

## Verificar que se subió

Ve a: https://github.com/marcos-recolons/whatsapp-ia-bot

Deberías ver todos los archivos del proyecto.

