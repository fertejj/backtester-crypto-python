import pandas as pd
from datetime import datetime
from typing import Optional


def format_currency(amount: float, decimals: int = 2) -> str:
    """Formatea un monto como moneda"""
    return f"${amount:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Formatea un valor como porcentaje"""
    return f"{value * 100:.{decimals}f}%"


def calculate_trade_duration(entry_time: pd.Timestamp, exit_time: pd.Timestamp) -> float:
    """Calcula la duración de un trade en horas"""
    if exit_time is None or entry_time is None:
        return 0.0
    
    duration = (exit_time - entry_time).total_seconds() / 3600
    return round(duration, 2)


def validate_date_range(start_date: str, end_date: str) -> bool:
    """Valida que el rango de fechas sea válido"""
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        return start_dt < end_dt
    except ValueError:
        return False


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """División segura que evita división por cero"""
    if denominator == 0:
        return default
    return numerator / denominator


def timestamp_to_string(timestamp: pd.Timestamp, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Convierte timestamp a string"""
    if pd.isna(timestamp):
        return "N/A"
    return timestamp.strftime(format)


def calculate_compound_return(returns: pd.Series) -> float:
    """Calcula el retorno compuesto de una serie de retornos"""
    if returns.empty:
        return 0.0
    return (1 + returns).prod() - 1


def get_trading_days_between(start_date: str, end_date: str) -> int:
    """Calcula los días de trading entre dos fechas"""
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Aproximación: considerar 5 días de trading por semana
    total_days = (end_dt - start_dt).days
    trading_days = int(total_days * 5 / 7)
    
    return max(1, trading_days)


def print_backtest_summary(results) -> None:
    """Imprime un resumen de los resultados del backtest"""
    print("=" * 60)
    print("RESUMEN DEL BACKTEST")
    print("=" * 60)
    
    print(f"Capital Inicial:      {format_currency(results.initial_capital)}")
    print(f"Capital Final:        {format_currency(results.final_capital)}")
    print(f"Retorno Total:        {format_currency(results.total_return)} ({format_percentage(results.total_return_pct)})")
    print()
    
    print(f"Total de Trades:      {results.total_trades}")
    print(f"Trades Ganadores:     {results.winning_trades}")
    print(f"Trades Perdedores:    {results.losing_trades}")
    print(f"Win Rate:             {format_percentage(results.win_rate)}")
    print()
    
    print(f"Ganancia Promedio:    {format_currency(results.avg_win)}")
    print(f"Pérdida Promedio:     {format_currency(results.avg_loss)}")
    print(f"Profit Factor:        {results.profit_factor:.2f}")
    print()
    
    print(f"Sharpe Ratio:         {results.sharpe_ratio:.2f}")
    print(f"Max Drawdown:         {format_currency(results.max_drawdown)} ({format_percentage(results.max_drawdown_pct)})")
    print(f"Calmar Ratio:         {results.calmar_ratio:.2f}")
    print("=" * 60)