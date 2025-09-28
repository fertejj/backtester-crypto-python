# 🔑 Configuración de API Real de BingX

## 📋 Pasos para usar datos reales

### 1. 🏦 Crear cuenta en BingX
- Ve a [https://bingx.com](https://bingx.com)
- Registra tu cuenta
- Completa la verificación KYC (opcional para API)

### 2. 🔐 Generar API Keys

1. **Accede a tu cuenta** en BingX
2. Ve a **API Management** en tu perfil
3. Haz clic en **Create API**
4. Configura los permisos:
   - ✅ **Read** (obligatorio para datos históricos)
   - ❌ **Trade** (NO necesario para backtesting)
   - ❌ **Withdraw** (NO necesario)
5. **Copia tus credenciales**:
   - API Key
   - Secret Key

### 3. 🔧 Configurar archivo .env

```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env con tus credenciales reales
nano .env
```

**Contenido de .env:**
```bash
# Variables de entorno para BingX API
BINGX_API_KEY=tu_api_key_real_aqui
BINGX_SECRET_KEY=tu_secret_key_real_aqui
BINGX_BASE_URL=https://open-api.bingx.com

# Configuración de backtesting  
DEFAULT_INITIAL_CAPITAL=10000
DEFAULT_COMMISSION=0.001
```

### 4. ⚠️ Seguridad IMPORTANTE

- **NUNCA** compartas tus API keys
- **NUNCA** subas el archivo .env a GitHub
- **NUNCA** hardcodees las keys en el código
- Usa **solo permisos de lectura** para backtesting
- Considera usar **API Testnet** para pruebas

### 5. 🚀 Probar conexión

```bash
# Ejecutar demo con API real
python demo_api_real.py

# O ejecutar la interfaz web
streamlit run app.py
```

## 📊 Símbolos disponibles

BingX usa el formato estándar:
- **Bitcoin**: BTCUSDT
- **Ethereum**: ETHUSDT  
- **Binance Coin**: BNBUSDT
- **Solana**: SOLUSDT
- **Cardano**: ADAUSDT
- **Polygon**: MATICUSDT

## ⏰ Intervalos soportados

- **1m, 5m, 15m, 30m** - Para scalping
- **1h, 4h** - Para swing trading  
- **1d** - Para análisis diario
- **1w** - Para tendencias semanales

## 🔍 Troubleshooting

### Error: "symbol: This field must end with -USDT or -USDC"
- **Solución**: Usar formato correcto como `BTCUSDT`

### Error: "API key y secret key son requeridos"  
- **Solución**: Verificar archivo .env y credenciales

### Error: "Invalid signature"
- **Solución**: Verificar que secret key sea correcto

### Error: "IP not in whitelist"
- **Solución**: En BingX, agregar tu IP a la whitelist

### Error: "Rate limit exceeded"
- **Solución**: Reducir frecuencia de requests (automático en el código)

## 🎯 Ventajas de datos reales

✅ **Datos precisos** de mercado real
✅ **Spreads reales** bid/ask
✅ **Volumen real** de trading
✅ **Gaps** y movimientos extremos
✅ **Backtests más confiables**

## 🔄 Fallback a datos sintéticos

Si no configuras API keys, el sistema automáticamente usa datos sintéticos para que puedas probar todas las funcionalidades.

---

**💡 Tip**: Comienza con datos sintéticos para familiarizarte con el sistema, luego configura la API real para backtests de producción.