# 🚀 Crypto Trading Backtester

[![CI](https://github.com/[tu-usuario]/backtester-cripto/workflows/CI/badge.svg)](https://github.com/[tu-usuario]/backtester-cripto/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Un backtester profesional para estrategias de trading de criptomonedas con **interfaz gráfica web** utilizando la API de BingX.

## ✨ Características Principales

### 🌐 **Interfaz Web Interactiva**
- **Streamlit Dashboard**: Interfaz moderna y fácil de usar
- **Configuración Dinámica**: Panel personalizado por estrategia  
- **Gráficos Interactivos**: Visualizaciones en tiempo real con Plotly
- **Múltiples Timeframes**: 5min, 15min, 30min, 1h, 4h, 1d, 1w

### 🎯 **Estrategias de Trading**
- **RSI Strategy**: Estrategia basada en índice de fuerza relativa
- **MACD Strategy**: Señales de convergencia/divergencia de medias móviles  
- **Bollinger Bands**: Trading en bandas de volatilidad
- **EMA Triple** ⭐ **NUEVA**: Triple crossover con EMAs (20/55/200)
- **EMA Golden Cross**: Cruce de medias móviles exponenciales

### � **Indicadores Técnicos Avanzados**
- **RSI, MACD, Bollinger Bands** usando librería `ta`
- **EMAs configurables** con múltiples períodos
- **Detección automática** de tendencias y señales

### ⚙️ **Motor de Backtesting**
- **API Integration**: Cliente personalizado para BingX con datos sintéticos
- **Position Management**: Gestión completa de posiciones long/short
- **Risk Management**: Stop loss, take profit, position sizing
- **Performance Metrics**: Sharpe ratio, drawdown, profit factor, win rate

## Estructura del Proyecto

```
backtester-cripto/
├── src/
│   ├── api/
│   │   └── bingx_client.py      # Cliente API de BingX
│   ├── indicators/
│   │   └── technical.py         # Indicadores técnicos
│   ├── strategies/
│   │   ├── base.py             # Estrategia base
│   │   └── rsi_strategy.py     # Estrategia ejemplo con RSI
│   ├── backtester/
│   │   ├── engine.py           # Motor de backtesting
│   │   └── metrics.py          # Cálculo de métricas
│   ├── risk/
│   │   └── manager.py          # Gestión de riesgo
│   ├── visualization/
│   │   └── charts.py           # Gráficos y visualizaciones
│   └── utils/
│       └── helpers.py          # Funciones auxiliares
├── config/
│   └── settings.py             # Configuración
├── examples/
│   └── basic_backtest.py       # Ejemplo de uso
├── tests/
│   └── test_indicators.py      # Tests unitarios
├── .env.example                # Ejemplo de variables de entorno
├── requirements.txt            # Dependencias
└── README.md                   # Documentación
```

## Instalación

1. Clona el repositorio:
```bash
git clone <repository-url>
cd backtester-cripto
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita .env con tu API key de BingX
```

## Uso

### 🌐 Interfaz Gráfica Web (Recomendado):

1. **Lanzar la aplicación web:**
```bash
# Opción 1: Desde VS Code
# Ctrl+Shift+P → "Tasks: Run Task" → "Launch Web App"

# Opción 2: Desde terminal
streamlit run app.py
```

2. **Abrir en el navegador:**
   - La aplicación se abrirá automáticamente en `http://localhost:8501`
   - Si no se abre, copia la URL del terminal

3. **Usar la interfaz:**
   - Configura los parámetros en el panel lateral
   - Selecciona la estrategia (RSI, MACD, Bollinger Bands)
   - Ajusta la gestión de riesgo
   - Haz clic en "🚀 Ejecutar Backtest"
   - Visualiza los resultados con gráficos interactivos

### 💻 Línea de Comandos:

```python
from src.api.bingx_client import BingXClient
from src.strategies.rsi_strategy import RSIStrategy
from src.backtester.engine import BacktesterEngine

# Configurar cliente API
client = BingXClient()

# Crear estrategia
strategy = RSIStrategy(
    symbol="BTCUSDT",
    rsi_period=14,
    buy_threshold=30,
    sell_threshold=70
)

# Ejecutar backtest
engine = BacktesterEngine(client)
results = engine.run_backtest(
    strategy=strategy,
    start_date="2024-01-01",
    end_date="2024-12-01",
    initial_capital=10000
)

# Mostrar resultados
print(f"Retorno Total: {results.total_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"Max Drawdown: {results.max_drawdown:.2%}")
```

## API de BingX

Para usar este backtester necesitas:
1. Cuenta en BingX
2. API Key y Secret Key
3. Configurar las credenciales en el archivo `.env`

## Desarrollo

Para ejecutar los tests:
```bash
pytest tests/
```

Para ejecutar el ejemplo:
```bash
python examples/basic_backtest.py
```

## Licencia

MIT License