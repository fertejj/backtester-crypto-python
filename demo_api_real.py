#!/usr/bin/env python3
"""
Demo de API Real de BingX
Muestra cómo usar datos históricos reales del mercado
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.bingx_client import BingXClient
from src.strategies.ema_strategy import EMAStrategy
from src.backtester.engine import BacktesterEngine
from src.risk.manager import RiskParameters


def test_api_real():
    """Prueba la conectividad con la API real de BingX"""
    
    print("🔌 Probando conexión con API Real de BingX")
    print("=" * 50)
    
    # Verificar si existe el archivo .env
    env_file = ".env"
    if not os.path.exists(env_file):
        print("❌ Archivo .env no encontrado")
        print("💡 Ejecuta: cp .env.example .env")
        print("💡 Luego edita .env con tus credenciales API")
        print("📚 Ver: API_REAL_SETUP.md para instrucciones completas")
        return False
    
    try:
        # Crear cliente con configuración del .env
        print("🔑 Inicializando cliente BingX...")
        client = BingXClient()
        
        # Probar obtener símbolos disponibles
        print("📊 Obteniendo símbolos disponibles...")
        symbols = client.get_symbols()
        
        if symbols:
            print(f"✅ Conexión exitosa! Encontrados {len(symbols)} símbolos")
            print("\n📋 Algunos símbolos disponibles:")
            
            # Mostrar primeros 10 símbolos USDT
            usdt_symbols = [s for s in symbols if s.get('symbol', '').endswith('USDT')][:10]
            for i, symbol in enumerate(usdt_symbols, 1):
                print(f"   {i}. {symbol.get('symbol')}")
                
        else:
            print("⚠️  No se encontraron símbolos")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con API: {e}")
        print("\n🔧 Posibles soluciones:")
        print("   1. Verificar credenciales API en .env")
        print("   2. Verificar conexión a internet")
        print("   3. Verificar que IP esté en whitelist de BingX")
        return False
    
    return True


def demo_datos_reales():
    """Demostración usando datos históricos reales"""
    
    print("\n🚀 Demo: Backtesting con Datos Reales")
    print("=" * 50)
    
    # Configuración
    symbol = "BTCUSDT"
    interval = "1h"  
    days_back = 30  # Últimos 30 días
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"📊 Configuración:")
    print(f"   Símbolo: {symbol}")
    print(f"   Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
    print(f"   Timeframe: {interval}")
    print()
    
    try:
        # Crear cliente  
        client = BingXClient(use_synthetic=False)  # Forzar datos reales
        
        # Obtener datos históricos
        print("📡 Descargando datos históricos reales...")
        data = client.get_historical_data(
            symbol=symbol,
            interval=interval,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        print(f"✅ Descargados {len(data)} registros históricos")
        print(f"📅 Período: {data.index[0]} a {data.index[-1]}")
        print(f"💰 Precio actual: ${data['close'].iloc[-1]:.2f}")
        print(f"📊 Rango de precios: ${data['low'].min():.2f} - ${data['high'].max():.2f}")
        
        # Ejecutar backtest con datos reales
        print("\n🔄 Ejecutando backtest con estrategia EMA...")
        
        engine = BacktesterEngine(api_client=client, commission=0.001)
        
        strategy = EMAStrategy(
            symbol=symbol,
            fast_ema=20,
            medium_ema=55,
            slow_ema=200,
            allow_longs=True,
            allow_shorts=False,  # Solo longs para demo
            trend_filter=True
        )
        
        risk_params = RiskParameters(
            max_position_size=0.2,
            stop_loss_pct=0.03,
            take_profit_pct=0.06,
            risk_per_trade=0.02
        )
        
        results = engine.run_backtest(
            strategy=strategy,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            initial_capital=10000,
            interval=interval,
            risk_params=risk_params
        )
        
        # Mostrar resultados
        print("\n📈 Resultados del Backtest:")
        print(f"   Retorno Total: ${results.total_return:,.2f} ({results.total_return_pct:.2f}%)")
        print(f"   Trades Ejecutados: {len(results.trades)}")
        print(f"   Win Rate: {results.win_rate:.2%}")
        print(f"   Sharpe Ratio: {results.sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {results.max_drawdown_pct:.2%}")
        
        # Análisis de trades
        closed_trades = [t for t in results.trades if not t.is_open]
        if closed_trades:
            winners = [t for t in closed_trades if t.pnl > 0]
            print(f"   Trades Ganadores: {len(winners)}")
            
            if winners:
                best_trade = max(winners, key=lambda x: x.pnl)
                print(f"   Mejor Trade: ${best_trade.pnl:.2f} ({best_trade.entry_time.strftime('%Y-%m-%d')})")
        
        print("\n✅ Demo completada con datos reales!")
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        print("🔄 Cambiando a datos sintéticos...")
        
        # Fallback a datos sintéticos
        client_synthetic = BingXClient(use_synthetic=True)
        print("📊 Ejecutando con datos sintéticos para comparación...")


def main():
    """Función principal"""
    
    print("🌟 BingX API Real - Sistema de Testing")
    print("=" * 60)
    
    # Probar conectividad
    if test_api_real():
        print("\n" + "="*60)
        
        # Preguntar si ejecutar demo completa
        response = input("\n🚀 ¿Ejecutar demo completa con backtest? (y/N): ")
        
        if response.lower() in ['y', 'yes', 'sí', 's']:
            demo_datos_reales()
        else:
            print("✅ Conexión verificada. Listo para usar API real!")
    else:
        print("\n🔄 Usando modo sintético por defecto")
        print("📚 Consulta API_REAL_SETUP.md para configurar API real")
    
    print(f"\n💡 Para usar la interfaz web: streamlit run app.py")
    print(f"🎨 Para demo gráficos: python demo_graficos.py")


if __name__ == "__main__":
    main()