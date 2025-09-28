from typing import Dict, List, Optional
from dataclasses import dataclass, field
import pandas as pd
import numpy as np


@dataclass
class Trade:
    """Representa una operación individual"""
    entry_time: pd.Timestamp
    exit_time: Optional[pd.Timestamp] = None
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    quantity: float = 0.0
    side: str = "long"  # "long" or "short"
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    commission: float = 0.0
    is_open: bool = True


@dataclass
class BacktestResults:
    """Resultados del backtest"""
    # Métricas generales
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    
    # Trades
    trades: List[Trade] = field(default_factory=list)
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # Métricas de riesgo/retorno
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    calmar_ratio: float = 0.0
    
    # Métricas de rendimiento
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    
    # Series temporales
    equity_curve: pd.Series = field(default_factory=pd.Series)
    drawdown_series: pd.Series = field(default_factory=pd.Series)
    
    def to_dict(self) -> Dict:
        """Convierte los resultados a diccionario"""
        return {
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'total_return_pct': self.total_return_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_pct': self.max_drawdown_pct,
            'calmar_ratio': self.calmar_ratio,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'profit_factor': self.profit_factor
        }


class PerformanceMetrics:
    """Calcula métricas de rendimiento para backtesting"""
    
    @staticmethod
    def calculate_returns(equity_curve: pd.Series) -> pd.Series:
        """Calcula retornos porcentuales"""
        return equity_curve.pct_change().fillna(0)
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calcula el Sharpe ratio"""
        if returns.std() == 0:
            return 0.0
        
        excess_returns = returns.mean() - risk_free_rate / 252  # Ajustar tasa libre de riesgo
        return (excess_returns / returns.std()) * np.sqrt(252)  # Anualizar
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> tuple:
        """Calcula el máximo drawdown absoluto y porcentual"""
        peak = equity_curve.expanding().max()
        drawdown = equity_curve - peak
        drawdown_pct = drawdown / peak
        
        max_dd = drawdown.min()
        max_dd_pct = drawdown_pct.min()
        
        return abs(max_dd), abs(max_dd_pct)
    
    @staticmethod
    def calculate_calmar_ratio(total_return: float, max_drawdown: float) -> float:
        """Calcula el Calmar ratio (retorno anual / max drawdown)"""
        if max_drawdown == 0:
            return 0.0
        return total_return / max_drawdown
    
    @staticmethod
    def calculate_trade_metrics(trades: List[Trade]) -> Dict:
        """Calcula métricas relacionadas con trades"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0
            }
        
        # Filtrar trades cerrados
        closed_trades = [t for t in trades if not t.is_open and t.pnl is not None]
        
        if not closed_trades:
            return {
                'total_trades': len(trades),
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0
            }
        
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl < 0]
        
        total_trades = len(closed_trades)
        num_winning = len(winning_trades)
        num_losing = len(losing_trades)
        win_rate = num_winning / total_trades if total_trades > 0 else 0.0
        
        avg_win = sum(t.pnl for t in winning_trades) / num_winning if num_winning > 0 else 0.0
        avg_loss = abs(sum(t.pnl for t in losing_trades) / num_losing) if num_losing > 0 else 0.0
        
        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': num_winning,
            'losing_trades': num_losing,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    @classmethod
    def calculate_all_metrics(cls, initial_capital: float, equity_curve: pd.Series, 
                            trades: List[Trade]) -> BacktestResults:
        """Calcula todas las métricas de rendimiento"""
        if equity_curve.empty:
            return BacktestResults(
                initial_capital=initial_capital,
                final_capital=initial_capital,
                total_return=0.0,
                total_return_pct=0.0
            )
        
        final_capital = equity_curve.iloc[-1]
        total_return = final_capital - initial_capital
        total_return_pct = total_return / initial_capital if initial_capital > 0 else 0.0
        
        # Calcular retornos
        returns = cls.calculate_returns(equity_curve)
        
        # Métricas de riesgo
        sharpe_ratio = cls.calculate_sharpe_ratio(returns)
        max_dd, max_dd_pct = cls.calculate_max_drawdown(equity_curve)
        calmar_ratio = cls.calculate_calmar_ratio(total_return_pct, max_dd_pct)
        
        # Métricas de trades
        trade_metrics = cls.calculate_trade_metrics(trades)
        
        # Serie de drawdown
        peak = equity_curve.expanding().max()
        drawdown_series = (equity_curve - peak) / peak
        
        return BacktestResults(
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            trades=trades,
            total_trades=trade_metrics['total_trades'],
            winning_trades=trade_metrics['winning_trades'],
            losing_trades=trade_metrics['losing_trades'],
            win_rate=trade_metrics['win_rate'],
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            calmar_ratio=calmar_ratio,
            avg_win=trade_metrics['avg_win'],
            avg_loss=trade_metrics['avg_loss'],
            profit_factor=trade_metrics['profit_factor'],
            equity_curve=equity_curve,
            drawdown_series=drawdown_series
        )