#!/usr/bin/env python3
"""
Test específico para verificar los gráficos de la aplicación
"""

import sys
import os
from datetime import datetime

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.bingx_client import BingXClient
from src.strategies.ema_strategy import EMAStrategy
from src.backtester.engine import BacktesterEngine
from src.risk.manager import RiskParameters
from src.visualization.charts import ChartGenerator
from src.indicators.technical import TechnicalIndicators


def test_grafico_app():
    """Test específico del gráfico que usa la app"""
    
    print("🔍 Test: Verificando Gráfico de la App")
    print("=" * 40)
    
    # Configuración igual a la app
    symbol = "BTCUSDT"
    interval = "1h"
    start_date = "2024-01-01"
    end_date = "2024-03-01"
    
    # Crear cliente sintético
    client = BingXClient(use_synthetic=True)
    
    # Crear estrategia
    strategy = EMAStrategy(
        symbol=symbol,
        fast_ema=20,
        medium_ema=55,
        slow_ema=200,
        allow_longs=True,
        allow_shorts=False,
        trend_filter=True
    )
    
    # Ejecutar backtest
    print("🔄 Ejecutando backtest...")
    engine = BacktesterEngine(api_client=client, commission=0.001)
    
    risk_params = RiskParameters(
        max_position_size=0.2,
        stop_loss_pct=0.03,
        take_profit_pct=0.06,
        risk_per_trade=0.02
    )
    
    results = engine.run_backtest(
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        initial_capital=10000,
        interval=interval,
        risk_params=risk_params
    )
    
    print(f"✅ Backtest completado. Trades: {len(results.trades)}")
    
    if not results.trades:
        print("❌ No hay trades para probar gráficos")
        return
    
    # Simular lo que hace la app
    print("\n📊 Probando función show_trading_signals_chart...")
    
    try:
        # 1. Crear chart generator
        chart_generator = ChartGenerator()
        
        # 2. Obtener fechas de trades
        first_trade = min(results.trades, key=lambda x: x.entry_time)
        last_trade = max(results.trades, key=lambda x: x.entry_time if x.entry_time else first_trade.entry_time)
        
        print(f"📅 Rango de trades: {first_trade.entry_time} a {last_trade.entry_time}")
        
        # 3. Obtener datos históricos (igual que la app)
        data = client.get_historical_data(
            symbol=symbol,
            interval="1h",
            start_date=first_trade.entry_time.strftime('%Y-%m-%d'),
            end_date=last_trade.entry_time.strftime('%Y-%m-%d') if last_trade.entry_time else first_trade.entry_time.strftime('%Y-%m-%d')
        )
        
        print(f"📊 Datos obtenidos: {len(data)} registros")
        print(f"   Rango de fechas: {data.index[0]} a {data.index[-1]}")
        print(f"   Columnas: {list(data.columns)}")
        
        # 4. Preparar indicadores EMA (igual que la app)
        indicators = {}
        tech_indicators = TechnicalIndicators()
        
        indicators['ema_20'] = tech_indicators.ema(data['close'], period=20)
        indicators['ema_55'] = tech_indicators.ema(data['close'], period=55)
        indicators['ema_200'] = tech_indicators.ema(data['close'], period=200)
        
        print(f"📈 Indicadores calculados: {list(indicators.keys())}")
        
        # 5. Generar gráfico avanzado (Tab 1)
        print("\n🎨 Generando gráfico avanzado...")
        fig_advanced = chart_generator.plot_trading_signals_advanced(
            data=data,
            trades=results.trades,
            indicators=indicators,
            symbol=symbol,
            title=f"EMA Triple Strategy - {symbol}"
        )
        
        print("✅ Gráfico avanzado creado exitosamente")
        
        # 6. Generar gráfico de análisis (Tab 2)
        print("🎯 Generando gráfico de análisis...")
        fig_simple = chart_generator.plot_trade_analysis(
            data=data,
            trades=results.trades,
            symbol=symbol
        )
        
        print("✅ Gráfico de análisis creado exitosamente")
        
        # 7. Verificar contenido de los gráficos
        print("\n🔍 Verificando contenido de gráficos:")
        print(f"   Gráfico avanzado: {len(fig_advanced.data)} trazos")
        print(f"   Gráfico análisis: {len(fig_simple.data)} trazos")
        
        # 8. Analizar trades para validar
        closed_trades = [t for t in results.trades if not t.is_open]
        long_trades = [t for t in closed_trades if t.side.lower() == 'long']
        short_trades = [t for t in closed_trades if t.side.lower() == 'short']
        
        print(f"\n📋 Análisis de trades:")
        print(f"   Trades cerrados: {len(closed_trades)}")
        print(f"   Longs: {len(long_trades)}")
        print(f"   Shorts: {len(short_trades)}")
        
        if closed_trades:
            winners = [t for t in closed_trades if t.pnl > 0]
            losers = [t for t in closed_trades if t.pnl <= 0]
            print(f"   Ganadores: {len(winners)}")
            print(f"   Perdedores: {len(losers)}")
        
        # 9. Guardar para inspección manual
        output_dir = "test_charts"
        os.makedirs(output_dir, exist_ok=True)
        
        fig_advanced.write_html(f"{output_dir}/test_advanced.html")
        fig_simple.write_html(f"{output_dir}/test_analysis.html")
        
        print(f"\n💾 Gráficos guardados en {output_dir}/")
        print("✅ Test completado exitosamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        print("📋 Traceback completo:")
        traceback.print_exc()
        return False


def test_funciones_individuales():
    """Test de las funciones de gráficos por separado"""
    
    print("\n🔧 Test: Funciones Individuales")
    print("=" * 40)
    
    try:
        from src.visualization.charts import ChartGenerator
        
        # Crear datos sintéticos simples
        client = BingXClient(use_synthetic=True)
        data = client.get_historical_data("BTCUSDT", "1h", "2024-01-01", "2024-01-05")
        
        print(f"📊 Datos sintéticos: {len(data)} registros")
        
        # Test plot_trading_signals_advanced
        chart_gen = ChartGenerator()
        
        # Crear trades de prueba
        from src.backtester.metrics import Trade
        import pandas as pd
        
        trades = [
            Trade(
                entry_time=data.index[10],
                entry_price=data['close'].iloc[10],
                exit_time=data.index[20],
                exit_price=data['close'].iloc[20],
                quantity=0.1,
                side="long",
                pnl=100.0,
                is_open=False
            ),
            Trade(
                entry_time=data.index[30],
                entry_price=data['close'].iloc[30],
                exit_time=data.index[40],
                exit_price=data['close'].iloc[40],
                quantity=0.1,
                side="long",
                pnl=-50.0,
                is_open=False
            )
        ]
        
        print(f"📈 Trades de prueba: {len(trades)}")
        
        # Test gráfico avanzado
        fig1 = chart_gen.plot_trading_signals_advanced(
            data=data,
            trades=trades,
            indicators=None,
            symbol="BTCUSDT",
            title="Test Avanzado"
        )
        
        print("✅ plot_trading_signals_advanced: OK")
        
        # Test gráfico de análisis
        fig2 = chart_gen.plot_trade_analysis(
            data=data,
            trades=trades,
            symbol="BTCUSDT"
        )
        
        print("✅ plot_trade_analysis: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test individual: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Test de Gráficos de la Aplicación")
    print("=" * 50)
    
    # Test principal
    success1 = test_grafico_app()
    
    # Test de funciones individuales
    success2 = test_funciones_individuales()
    
    print(f"\n📊 Resultados:")
    print(f"   Test principal: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Test individual: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 Todos los tests pasaron!")
        print("💡 Los gráficos de la app deberían funcionar correctamente")
    else:
        print("\n⚠️  Algunos tests fallaron")
        print("🔧 Revisa los errores arriba para diagnosticar el problema")