#!/usr/bin/env python3
"""
Demo de visualización de gráficos con señales Long/Short
Muestra las nuevas capacidades gráficas del backtester
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.bingx_client import BingXClient
from src.strategies.ema_strategy import EMAStrategy
from src.backtester.engine import BacktesterEngine
from src.risk.manager import RiskParameters
from src.visualization.charts import ChartGenerator
from src.indicators.technical import TechnicalIndicators


def demo_graficos_trading():
    """Demostración de los nuevos gráficos con señales Long/Short"""
    
    print("🚀 Demo: Gráficos Avanzados de Trading")
    print("=====================================")
    
    # Configuración
    symbol = "BTCUSDT"
    interval = "1h"
    start_date = "2024-01-01"
    end_date = "2024-03-01"
    initial_capital = 10000
    
    print(f"📊 Configuración:")
    print(f"   Símbolo: {symbol}")
    print(f"   Período: {start_date} a {end_date}")
    print(f"   Timeframe: {interval}")
    print(f"   Capital: ${initial_capital:,}")
    print()
    
    # Crear cliente y motor  
    client = BingXClient(api_key="demo", secret_key="demo")  # Usar datos sintéticos
    engine = BacktesterEngine(api_client=client, commission=0.001)
    
    # Estrategia EMA Triple
    strategy = EMAStrategy(
        symbol=symbol,
        fast_ema=20,
        medium_ema=55, 
        slow_ema=200,
        allow_longs=True,
        allow_shorts=True,
        trend_filter=True
    )
    
    # Parámetros de riesgo
    risk_params = RiskParameters(
        max_position_size=0.2,  # 20% del capital
        stop_loss_pct=0.03,     # 3% stop loss
        take_profit_pct=0.06,   # 6% take profit
        risk_per_trade=0.02     # 2% riesgo por trade
    )
    
    print("🔄 Ejecutando backtest...")
    
    # Ejecutar backtest
    results = engine.run_backtest(
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        interval=interval,
        risk_params=risk_params
    )
    
    print("✅ Backtest completado!")
    print()
    
    # Mostrar estadísticas básicas
    print("📈 Resultados:")
    print(f"   Retorno Total: ${results.total_return:,.2f} ({results.total_return_pct:.2f}%)")
    print(f"   Trades Totales: {len(results.trades)}")
    print(f"   Win Rate: {results.win_rate:.2%}")
    print(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
    print(f"   Max Drawdown: {results.max_drawdown_pct:.2%}")
    print()
    
    # Separar trades por tipo y resultado
    closed_trades = [t for t in results.trades if not t.is_open]
    
    if not closed_trades:
        print("⚠️ No hay trades cerrados para analizar")
        return
    
    # Análisis de trades
    long_trades = [t for t in closed_trades if t.side.lower() == 'long']
    short_trades = [t for t in closed_trades if t.side.lower() == 'short']
    
    winning_longs = [t for t in long_trades if t.pnl > 0]
    losing_longs = [t for t in long_trades if t.pnl <= 0]
    winning_shorts = [t for t in short_trades if t.pnl > 0]
    losing_shorts = [t for t in short_trades if t.pnl <= 0]
    
    print("🎯 Análisis de Señales:")
    print(f"   🟢 Longs Ganadores: {len(winning_longs)}")
    print(f"   🔴 Longs Perdedores: {len(losing_longs)}")
    print(f"   🟠 Shorts Ganadores: {len(winning_shorts)}")  
    print(f"   🔴 Shorts Perdedores: {len(losing_shorts)}")
    
    if long_trades:
        long_win_rate = len(winning_longs) / len(long_trades) * 100
        print(f"   📊 Long Win Rate: {long_win_rate:.1f}%")
    
    if short_trades:
        short_win_rate = len(winning_shorts) / len(short_trades) * 100
        print(f"   📊 Short Win Rate: {short_win_rate:.1f}%")
    
    print()
    
    # Obtener datos para gráficos
    print("📊 Generando gráficos...")
    
    # Obtener datos históricos (usar datos sintéticos directamente)
    print("📊 Generando datos sintéticos para gráficos...")
    data = client.get_historical_data(
        symbol=symbol,
        interval=interval,
        start_date=start_date,
        end_date=end_date
    )
    
    # Calcular indicadores
    tech_indicators = TechnicalIndicators()
    indicators = {
        'ema_20': tech_indicators.ema(data['close'], period=20),
        'ema_55': tech_indicators.ema(data['close'], period=55),
        'ema_200': tech_indicators.ema(data['close'], period=200)
    }
    
    # Crear generador de gráficos
    chart_generator = ChartGenerator()
    
    # Gráfico avanzado con señales
    print("🎨 Creando gráfico avanzado...")
    fig_advanced = chart_generator.plot_trading_signals_advanced(
        data=data,
        trades=results.trades,
        indicators=indicators,
        symbol=symbol,
        title=f"EMA Triple Strategy - {symbol} ({interval})"
    )
    
    # Gráfico de análisis de trades
    print("🎯 Creando gráfico de análisis...")
    fig_analysis = chart_generator.plot_trade_analysis(
        data=data,
        trades=results.trades,
        symbol=symbol
    )
    
    # Guardar gráficos
    output_dir = "charts_output"
    os.makedirs(output_dir, exist_ok=True)
    
    advanced_path = os.path.join(output_dir, f"{symbol}_advanced_signals.html")
    analysis_path = os.path.join(output_dir, f"{symbol}_trade_analysis.html")
    
    fig_advanced.write_html(advanced_path)
    fig_analysis.write_html(analysis_path)
    
    print("✅ Gráficos generados exitosamente!")
    print(f"   📁 Gráfico avanzado: {advanced_path}")
    print(f"   📁 Análisis de trades: {analysis_path}")
    print()
    
    # Mostrar mejores y peores trades
    print("💰 Top 5 Mejores Trades:")
    best_trades = sorted(closed_trades, key=lambda x: x.pnl, reverse=True)[:5]
    for i, trade in enumerate(best_trades, 1):
        trade_type = "🟢 LONG" if trade.side.lower() == 'long' else "🔴 SHORT"
        print(f"   {i}. {trade_type} - P&L: ${trade.pnl:.2f} ({trade.entry_time.strftime('%Y-%m-%d')})")
    
    print()
    print("📉 Top 5 Peores Trades:")
    worst_trades = sorted(closed_trades, key=lambda x: x.pnl)[:5]
    for i, trade in enumerate(worst_trades, 1):
        trade_type = "🟢 LONG" if trade.side.lower() == 'long' else "🔴 SHORT"
        print(f"   {i}. {trade_type} - P&L: ${trade.pnl:.2f} ({trade.entry_time.strftime('%Y-%m-%d')})")
    
    print()
    print("🎉 Demo completada!")
    print(f"💡 Abre los archivos HTML para ver los gráficos interactivos")
    print(f"🌐 O ejecuta 'streamlit run app.py' para la interfaz web completa")


if __name__ == "__main__":
    demo_graficos_trading()