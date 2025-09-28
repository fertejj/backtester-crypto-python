import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.visualization.plotly_professional import create_professional_plotly_chart
from src.backtester.metrics import Trade

# Configuración de página
st.set_page_config(page_title="Test Señales Claras", page_icon="🎯", layout="wide")

st.title("🎯 Test de Señales de Trading - MUY VISIBLES")

# Generar datos de prueba más realistas
np.random.seed(42)
dates = pd.date_range(start='2024-01-01', periods=500, freq='h')

# Crear datos con tendencia
base_price = 50000
price_trend = np.cumsum(np.random.randn(len(dates)) * 20)
noise = np.random.randn(len(dates)) * 100

prices = base_price + price_trend + noise

data = pd.DataFrame(index=dates)
data['open'] = prices
data['close'] = prices + np.random.randn(len(dates)) * 50
data['high'] = np.maximum(data['open'], data['close']) + np.abs(np.random.randn(len(dates)) * 30)
data['low'] = np.minimum(data['open'], data['close']) - np.abs(np.random.randn(len(data)) * 30)
data['volume'] = np.random.uniform(1000, 5000, len(data))

st.write(f"📊 Datos generados: {len(data)} barras de {dates[0].strftime('%Y-%m-%d')} a {dates[-1].strftime('%Y-%m-%d')}")

# Crear trades de ejemplo con diferentes tipos
trades = []

# LONG trades con ganancias y pérdidas
long_entries = [50, 150, 250, 350]
for i, entry_idx in enumerate(long_entries):
    entry_time = dates[entry_idx]
    exit_time = dates[entry_idx + 20 + i*5]  # Diferentes duraciones
    
    entry_price = float(data.iloc[entry_idx]['close'])
    
    # Alternar entre ganancia y pérdida
    if i % 2 == 0:
        # Ganancia
        exit_price = entry_price * (1 + np.random.uniform(0.02, 0.08))
    else:
        # Pérdida  
        exit_price = entry_price * (1 - np.random.uniform(0.01, 0.04))
    
    pnl = exit_price - entry_price
    
    trade = Trade(
        entry_time=entry_time,
        entry_price=entry_price,
        side='long',
        quantity=1.0,
        exit_time=exit_time,
        exit_price=exit_price,
        pnl=pnl
    )
    trades.append(trade)

# SHORT trades
short_entries = [100, 200, 300, 400]
for i, entry_idx in enumerate(short_entries):
    entry_time = dates[entry_idx]
    exit_time = dates[entry_idx + 15 + i*3]
    
    entry_price = float(data.iloc[entry_idx]['close'])
    
    # Alternar entre ganancia y pérdida para shorts
    if i % 2 == 0:
        # Ganancia (precio baja)
        exit_price = entry_price * (1 - np.random.uniform(0.01, 0.05))
        pnl = entry_price - exit_price  # Para shorts, ganancia cuando precio baja
    else:
        # Pérdida (precio sube)
        exit_price = entry_price * (1 + np.random.uniform(0.01, 0.03))
        pnl = entry_price - exit_price  # Será negativo
    
    trade = Trade(
        entry_time=entry_time,
        entry_price=entry_price,
        side='short',
        quantity=1.0,
        exit_time=exit_time,
        exit_price=exit_price,
        pnl=pnl
    )
    trades.append(trade)

# Ordenar trades por tiempo
trades.sort(key=lambda x: x.entry_time)

st.write(f"🎯 Trades creados: {len(trades)} ({len([t for t in trades if t.side=='long'])} LONG, {len([t for t in trades if t.side=='short'])} SHORT)")

# Mostrar estadísticas
profitable = [t for t in trades if t.pnl > 0]
st.write(f"💰 Trades rentables: {len(profitable)}/{len(trades)} ({len(profitable)/len(trades)*100:.1f}%)")

# Crear indicadores simples para el test
ema_20 = data['close'].ewm(span=20).mean()
ema_50 = data['close'].ewm(span=50).mean()

indicators = {
    'ema_20': ema_20,
    'ema_50': ema_50
}

st.markdown("---")
st.subheader("📊 Gráfico con Señales MUY VISIBLES")

# Crear el gráfico profesional
create_professional_plotly_chart(
    data=data,
    trades=trades,
    symbol="TEST-BTC",
    indicators=indicators
)

# Información adicional
st.markdown("---")
st.info("""
🔍 **Verificación de Señales:**
1. Las señales de **ENTRADA** deben aparecer claramente en el gráfico
2. Las señales de **SALIDA** deben estar conectadas con líneas punteadas
3. Los colores deben distinguir claramente entre LONG (verde) y SHORT (rojo)
4. Las áreas sombreadas muestran la duración de cada trade
5. El hover debe mostrar información detallada de cada señal
""")

st.success("✅ **Test completado** - Verifica que todas las señales sean claramente visibles en el gráfico")