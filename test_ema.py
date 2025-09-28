#!/usr/bin/env python3
"""
Script para probar la nueva estrategia EMA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.strategies.ema_strategy import EMAStrategy
from src.backtester.engine import BacktesterEngine
from src.risk.manager import RiskParameters
from src.utils.helpers import print_backtest_summary


def test_ema_strategy():
    """Test rápido de la estrategia EMA"""
    print("🧪 Probando Estrategia EMA Triple...")
    
    # Crear estrategia EMA
    strategy = EMAStrategy(
        symbol="BTCUSDT",
        fast_ema=20,
        medium_ema=55,
        slow_ema=200,
        min_trend_strength=0.001,
        allow_longs=True,
        allow_shorts=False,
        trend_filter=True
    )
    
    # Motor de backtesting
    engine = BacktesterEngine(api_client=None, commission=0.001)
    
    # Parámetros de riesgo
    risk_params = RiskParameters(
        max_position_size=0.15,
        stop_loss_pct=0.03,
        take_profit_pct=0.08,
        risk_per_trade=0.015
    )
    
    # Ejecutar backtest
    results = engine.run_backtest(
        strategy=strategy,
        start_date="2024-01-01",
        end_date="2024-06-01",
        initial_capital=10000,
        interval="5m",  # Usar 5 minutos
        risk_params=risk_params
    )
    
    print_backtest_summary(results)
    
    return results


if __name__ == "__main__":
    test_ema_strategy()