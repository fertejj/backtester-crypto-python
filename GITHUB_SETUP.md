# 🐙 Guía Completa: Configurar GitHub para Backtester Cripto

## 📋 **Paso a Paso**

### 1. 🔧 **Configurar Git Local** (REQUERIDO)
```bash
# Configura tu identidad (reemplaza con tu información)
git config --global user.name "Tu Nombre Completo"
git config --global user.email "tu.email@gmail.com"

# Verificar configuración
git config --global --list
```

### 2. 🌐 **Crear Repositorio en GitHub**

#### **Opción A: Desde GitHub Web**
1. Ve a [github.com](https://github.com)
2. Haz clic en **"New repository"** (botón verde)
3. **Repository name**: `backtester-cripto`
4. **Description**: `🚀 Backtester profesional para estrategias de trading de criptomonedas`
5. ✅ **Public** (recomendado para portfolio)
6. ❌ **NO** marques "Add a README file" (ya tienes uno)
7. ❌ **NO** marques "Add .gitignore" (ya tienes uno)
8. **License**: MIT (ya tienes LICENSE file)
9. Haz clic **"Create repository"**

#### **Opción B: Desde Terminal (GitHub CLI)**
```bash
# Instalar GitHub CLI si no lo tienes
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Autenticar y crear repo
gh auth login
gh repo create backtester-cripto --public --description "🚀 Backtester profesional para estrategias de trading de criptomonedas"
```

### 3. 🔗 **Conectar Local con GitHub**
```bash
cd /home/fernando/Desktop/backtester-cripto

# Agregar remote origin (reemplaza [tu-usuario] con tu username de GitHub)
git remote add origin https://github.com/[tu-usuario]/backtester-cripto.git

# Verificar remote
git remote -v
```

### 4. 📤 **Subir Código a GitHub**
```bash
# Hacer commit inicial
git add .
git commit -m "🎉 Initial commit: Crypto Trading Backtester

✨ Features:
- Streamlit web interface with dynamic strategy panels
- Multiple trading strategies (RSI, MACD, Bollinger, EMA Triple)  
- Technical indicators using 'ta' library
- Complete backtesting engine with risk management
- Support for multiple timeframes (5m, 15m, 30m, 1h, 4h, 1d, 1w)
- Interactive charts with Plotly
- Comprehensive test suite
- GitHub Actions CI/CD pipeline"

# Subir a GitHub
git branch -M main
git push -u origin main
```

### 5. ⚙️ **Configurar GitHub Actions** (Automático)
Los archivos ya están listos:
- `.github/workflows/ci.yml` - CI/CD pipeline
- Tests automáticos en cada push
- Soporte para Python 3.9-3.12
- Verificación de código con black y flake8

### 6. 📝 **Actualizar Badges en README**
Después de crear el repo, actualiza en `README.md`:
```markdown
[![CI](https://github.com/[tu-usuario]/backtester-cripto/workflows/CI/badge.svg)]
```
Reemplaza `[tu-usuario]` con tu username real.

## 🔐 **Configurar SSH (Recomendado)**

### **Generar Clave SSH**
```bash
# Generar nueva clave SSH
ssh-keygen -t ed25519 -C "tu.email@gmail.com"

# Agregar al ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Mostrar clave pública para copiar
cat ~/.ssh/id_ed25519.pub
```

### **Agregar a GitHub**
1. Ve a GitHub → Settings → SSH and GPG keys
2. Clic "New SSH key"
3. Pega la clave pública
4. Título: "Mi PC Linux"

### **Usar SSH en lugar de HTTPS**
```bash
# Cambiar remote a SSH
git remote set-url origin git@github.com:[tu-usuario]/backtester-cripto.git
```

## 🚀 **Comandos Finales**

Una vez configurado todo:

```bash
# Estado del repositorio
git status

# Ver archivos modificados
git log --oneline

# Push futuros cambios
git add .
git commit -m "✨ Descripción del cambio"
git push
```

## 🎯 **Próximos Pasos**

1. **⭐ Estrella tu repo** para que aparezca en tu perfil
2. **📋 Crear Issues** para nuevas funcionalidades
3. **🔀 Crear Branches** para cada nueva feature
4. **📈 Agregar más estrategias** y mejorar el backtester
5. **📊 Compartir resultados** en la comunidad

## 🐛 **Solución de Problemas**

### **Error: Permission denied (publickey)**
```bash
# Verificar SSH
ssh -T git@github.com
```

### **Error: Repository not found**
```bash
# Verificar remote
git remote -v
git remote set-url origin https://github.com/[usuario-correcto]/backtester-cripto.git
```

### **Error: Authentication failed**
```bash
# Usar token personal en lugar de contraseña
# GitHub → Settings → Developer settings → Personal access tokens
```

¡Tu backtester ya estará listo para GitHub! 🎉