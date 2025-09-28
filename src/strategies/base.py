from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd


class SignalType(Enum):
    """Tipos de señales de trading"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class TradeSignal:
    """Señal de trading"""
    timestamp: pd.Timestamp
    signal_type: SignalType
    price: float
    confidence: float = 1.0  # 0.0 a 1.0
    reason: str = ""
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class BaseStrategy(ABC):
    """Clase base para estrategias de trading"""
    
    def __init__(self, symbol: str, **kwargs):
        self.symbol = symbol
        self.parameters = kwargs
        self.signals: List[TradeSignal] = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[TradeSignal]:
        """
        Genera señales de trading basadas en los datos
        
        Args:
            data: DataFrame con datos OHLCV e indicadores
            
        Returns:
            Lista de señales de trading
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia"""
        pass
    
    def get_parameters(self) -> Dict:
        """Retorna los parámetros de la estrategia"""
        return self.parameters.copy()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Valida que los datos tengan las columnas necesarias"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_columns)
    
    def filter_signals_by_time(self, start_time: pd.Timestamp, 
                              end_time: pd.Timestamp) -> List[TradeSignal]:
        """Filtra señales por rango de tiempo"""
        return [
            signal for signal in self.signals 
            if start_time <= signal.timestamp <= end_time
        ]
    
    def get_signal_summary(self) -> Dict:
        """Retorna un resumen de las señales generadas"""
        buy_signals = [s for s in self.signals if s.signal_type == SignalType.BUY]
        sell_signals = [s for s in self.signals if s.signal_type == SignalType.SELL]
        
        return {
            'total_signals': len(self.signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'avg_confidence': sum(s.confidence for s in self.signals) / len(self.signals) if self.signals else 0
        }