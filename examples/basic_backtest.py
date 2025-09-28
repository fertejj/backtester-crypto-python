from src.api.bingx_client import BingXClient
from src.strategies.rsi_strategy import RSIStrategy, MACDStrategy
from src.backtester.engine import BacktesterEngine
from src.risk.manager import RiskParameters
from src.utils.helpers import print_backtest_summary
from config.settings import settings


def main():
    """Ejemplo básico de uso del backtester"""
    print("🚀 Crypto Trading Backtester - Ejemplo Básico")
    print("-" * 50)
    
    # Configurar parámetros
    symbol = "BTCUSDT"
    start_date = "2024-01-01"
    end_date = "2024-06-01"
    initial_capital = 10000
    
    try:
        # Crear cliente API (opcional - usará datos sintéticos si no está configurado)
        api_client = None
        if settings.bingx_api_key and settings.bingx_secret_key:
            api_client = BingXClient()
            print("✅ Cliente API de BingX configurado")
        else:
            print("⚠️  Cliente API no configurado - usando datos sintéticos")
        
        # Crear motor de backtesting
        engine = BacktesterEngine(api_client=api_client, commission=0.001)
        
        # Ejemplo 1: Estrategia RSI
        print(f"\n📊 Testeando Estrategia RSI para {symbol}")
        rsi_strategy = RSIStrategy(
            symbol=symbol,
            rsi_period=14,
            buy_threshold=30,
            sell_threshold=70
        )
        
        # Parámetros de riesgo
        risk_params = RiskParameters(
            max_position_size=0.2,  # 20% del capital por posición
            stop_loss_pct=0.05,     # Stop loss al 5%
            take_profit_pct=0.10,   # Take profit al 10%
            risk_per_trade=0.02     # 2% de riesgo por trade
        )
        
        # Ejecutar backtest
        rsi_results = engine.run_backtest(
            strategy=rsi_strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            interval="1h",
            risk_params=risk_params
        )
        
        print("\n📈 Resultados Estrategia RSI:")
        print_backtest_summary(rsi_results)
        
        # Ejemplo 2: Estrategia MACD
        print(f"\n📊 Testeando Estrategia MACD para {symbol}")
        macd_strategy = MACDStrategy(
            symbol=symbol,
            fast_period=12,
            slow_period=26,
            signal_period=9
        )
        
        macd_results = engine.run_backtest(
            strategy=macd_strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            interval="1h",
            risk_params=risk_params
        )
        
        print("\n📈 Resultados Estrategia MACD:")
        print_backtest_summary(macd_results)
        
        # Comparar estrategias
        print("\n🔍 Comparación de Estrategias:")
        print("-" * 40)
        print(f"{'Métrica':<20} {'RSI':<15} {'MACD':<15}")
        print("-" * 40)
        print(f"{'Retorno Total':<20} {rsi_results.total_return_pct*100:>12.2f}% {macd_results.total_return_pct*100:>12.2f}%")
        print(f"{'Sharpe Ratio':<20} {rsi_results.sharpe_ratio:>12.2f} {macd_results.sharpe_ratio:>12.2f}")
        print(f"{'Max Drawdown':<20} {rsi_results.max_drawdown_pct*100:>12.2f}% {macd_results.max_drawdown_pct*100:>12.2f}%")
        print(f"{'Win Rate':<20} {rsi_results.win_rate*100:>12.2f}% {macd_results.win_rate*100:>12.2f}%")
        print(f"{'Total Trades':<20} {rsi_results.total_trades:>12} {macd_results.total_trades:>12}")
        
        # Determinar mejor estrategia
        if rsi_results.sharpe_ratio > macd_results.sharpe_ratio:
            print(f"\n🏆 Mejor estrategia: RSI (Sharpe Ratio: {rsi_results.sharpe_ratio:.2f})")
        elif macd_results.sharpe_ratio > rsi_results.sharpe_ratio:
            print(f"\n🏆 Mejor estrategia: MACD (Sharpe Ratio: {macd_results.sharpe_ratio:.2f})")
        else:
            print("\n🤝 Las estrategias tienen rendimiento similar")
        
        print("\n✅ Backtest completado exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   - Optimiza los parámetros de las estrategias")
        print("   - Prueba con diferentes intervalos de tiempo")
        print("   - Implementa más estrategias")
        print("   - Analiza los gráficos de rendimiento")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando backtest: {e}")
        print("   Verifica la configuración y conexión a internet")


if __name__ == "__main__":
    main()