import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.visualization.tradingview_simple import create_simple_tradingview_chart
from src.backtester.metrics import Trade

# Generar datos de prueba
st.title("🧪 Test TradingView Chart")

# Crear datos sintéticos simples
dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='H')
np.random.seed(42)

data = pd.DataFrame({
    'open': 50000 + np.cumsum(np.random.randn(len(dates)) * 100),
    'high': 0,
    'low': 0,
    'close': 0
}, index=dates)

# Calcular high, low y close basado en open
data['close'] = data['open'] + np.random.randn(len(data)) * 50
data['high'] = np.maximum(data['open'], data['close']) + np.abs(np.random.randn(len(data)) * 25)
data['low'] = np.minimum(data['open'], data['close']) - np.abs(np.random.randn(len(data)) * 25)

st.write(f"Datos generados: {len(data)} barras")
st.write(data.head())

# Crear algunos trades de prueba
trades = [
    Trade(
        entry_time=dates[10],
        entry_price=float(data.iloc[10]['close']),
        side='long',
        quantity=1.0,
        exit_time=dates[20],
        exit_price=float(data.iloc[20]['close']),
        pnl=float(data.iloc[20]['close'] - data.iloc[10]['close'])
    ),
    Trade(
        entry_time=dates[50],
        entry_price=float(data.iloc[50]['close']),
        side='short',
        quantity=1.0,
        exit_time=dates[60],
        exit_price=float(data.iloc[60]['close']),
        pnl=float(data.iloc[50]['close'] - data.iloc[60]['close'])
    )
]

st.write(f"Trades generados: {len(trades)}")

# Mostrar gráfico TradingView
st.subheader("📊 Gráfico TradingView")
create_simple_tradingview_chart(data, trades, "TESTBTC")