import pandas as pd
from typing import List
from .base import BaseStrategy, TradeSignal, SignalType
from src.indicators.technical import TechnicalIndicators


class RSIStrategy(BaseStrategy):
    """
    Estrategia basada en RSI (Relative Strength Index)
    
    Señales:
    - BUY: RSI < buy_threshold (sobreventa)
    - SELL: RSI > sell_threshold (sobrecompra)
    """
    
    def __init__(self, symbol: str, rsi_period: int = 14, buy_threshold: float = 30, 
                 sell_threshold: float = 70, **kwargs):
        super().__init__(symbol, **kwargs)
        self.rsi_period = rsi_period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        
    def generate_signals(self, data: pd.DataFrame) -> List[TradeSignal]:
        """Genera señales basadas en RSI"""
        if not self.validate_data(data):
            raise ValueError("Datos inválidos: faltan columnas OHLCV")
        
        # Calcular RSI si no está presente
        if 'rsi' not in data.columns:
            data['rsi'] = TechnicalIndicators.rsi(data['close'], self.rsi_period)
        
        signals = []
        position = None  # None, 'long', 'short'
        
        for i in range(1, len(data)):
            current_rsi = data.iloc[i]['rsi']
            previous_rsi = data.iloc[i-1]['rsi']
            current_price = data.iloc[i]['close']
            timestamp = data.index[i]
            
            # Skip si RSI es NaN
            if pd.isna(current_rsi) or pd.isna(previous_rsi):
                continue
            
            # Señal de compra: RSI cruza desde abajo el umbral de compra
            if (previous_rsi >= self.buy_threshold and 
                current_rsi < self.buy_threshold and 
                position != 'long'):
                
                confidence = (self.buy_threshold - current_rsi) / self.buy_threshold
                confidence = max(0.1, min(1.0, confidence))
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.BUY,
                    price=current_price,
                    confidence=confidence,
                    reason=f"RSI oversold: {current_rsi:.2f} < {self.buy_threshold}"
                )
                signals.append(signal)
                position = 'long'
            
            # Señal de venta: RSI cruza desde arriba el umbral de venta
            elif (previous_rsi <= self.sell_threshold and 
                  current_rsi > self.sell_threshold and 
                  position == 'long'):
                
                confidence = (current_rsi - self.sell_threshold) / (100 - self.sell_threshold)
                confidence = max(0.1, min(1.0, confidence))
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.SELL,
                    price=current_price,
                    confidence=confidence,
                    reason=f"RSI overbought: {current_rsi:.2f} > {self.sell_threshold}"
                )
                signals.append(signal)
                position = None
        
        self.signals = signals
        return signals
    
    def get_strategy_name(self) -> str:
        return f"RSI Strategy (period={self.rsi_period}, buy<{self.buy_threshold}, sell>{self.sell_threshold})"


class MACDStrategy(BaseStrategy):
    """
    Estrategia basada en MACD
    
    Señales:
    - BUY: MACD cruza por encima de la señal
    - SELL: MACD cruza por debajo de la señal
    """
    
    def __init__(self, symbol: str, fast_period: int = 12, slow_period: int = 26, 
                 signal_period: int = 9, **kwargs):
        super().__init__(symbol, **kwargs)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def generate_signals(self, data: pd.DataFrame) -> List[TradeSignal]:
        """Genera señales basadas en MACD"""
        if not self.validate_data(data):
            raise ValueError("Datos inválidos: faltan columnas OHLCV")
        
        # Calcular MACD si no está presente
        if 'macd' not in data.columns:
            macd_data = TechnicalIndicators.macd(
                data['close'], self.fast_period, self.slow_period, self.signal_period
            )
            data['macd'] = macd_data['macd']
            data['macd_signal'] = macd_data['signal']
            data['macd_histogram'] = macd_data['histogram']
        
        signals = []
        position = None
        
        for i in range(1, len(data)):
            current_macd = data.iloc[i]['macd']
            current_signal = data.iloc[i]['macd_signal']
            previous_macd = data.iloc[i-1]['macd']
            previous_signal = data.iloc[i-1]['macd_signal']
            current_price = data.iloc[i]['close']
            timestamp = data.index[i]
            
            if pd.isna(current_macd) or pd.isna(current_signal):
                continue
            
            # Señal de compra: MACD cruza por encima de la señal
            if (previous_macd <= previous_signal and 
                current_macd > current_signal and 
                position != 'long'):
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.BUY,
                    price=current_price,
                    confidence=0.8,
                    reason="MACD bullish crossover"
                )
                signals.append(signal)
                position = 'long'
            
            # Señal de venta: MACD cruza por debajo de la señal
            elif (previous_macd >= previous_signal and 
                  current_macd < current_signal and 
                  position == 'long'):
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.SELL,
                    price=current_price,
                    confidence=0.8,
                    reason="MACD bearish crossover"
                )
                signals.append(signal)
                position = None
        
        self.signals = signals
        return signals
    
    def get_strategy_name(self) -> str:
        return f"MACD Strategy ({self.fast_period},{self.slow_period},{self.signal_period})"


class BollingerBandsStrategy(BaseStrategy):
    """
    Estrategia basada en Bollinger Bands
    
    Señales:
    - BUY: Precio toca la banda inferior
    - SELL: Precio toca la banda superior
    """
    
    def __init__(self, symbol: str, bb_period: int = 20, bb_std: float = 2.0, **kwargs):
        super().__init__(symbol, **kwargs)
        self.bb_period = bb_period
        self.bb_std = bb_std
        
    def generate_signals(self, data: pd.DataFrame) -> List[TradeSignal]:
        """Genera señales basadas en Bollinger Bands"""
        if not self.validate_data(data):
            raise ValueError("Datos inválidos: faltan columnas OHLCV")
        
        # Calcular Bollinger Bands si no están presentes
        if 'bb_lower' not in data.columns:
            bb_data = TechnicalIndicators.bollinger_bands(
                data['close'], self.bb_period, self.bb_std
            )
            data['bb_upper'] = bb_data['upper']
            data['bb_middle'] = bb_data['middle']
            data['bb_lower'] = bb_data['lower']
        
        signals = []
        position = None
        
        for i in range(1, len(data)):
            current_price = data.iloc[i]['close']
            previous_price = data.iloc[i-1]['close']
            current_lower = data.iloc[i]['bb_lower']
            current_upper = data.iloc[i]['bb_upper']
            previous_lower = data.iloc[i-1]['bb_lower']
            previous_upper = data.iloc[i-1]['bb_upper']
            timestamp = data.index[i]
            
            if pd.isna(current_lower) or pd.isna(current_upper):
                continue
            
            # Señal de compra: precio toca banda inferior
            if (previous_price > previous_lower and 
                current_price <= current_lower and 
                position != 'long'):
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.BUY,
                    price=current_price,
                    confidence=0.7,
                    reason="Price touched lower Bollinger Band"
                )
                signals.append(signal)
                position = 'long'
            
            # Señal de venta: precio toca banda superior
            elif (previous_price < previous_upper and 
                  current_price >= current_upper and 
                  position == 'long'):
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.SELL,
                    price=current_price,
                    confidence=0.7,
                    reason="Price touched upper Bollinger Band"
                )
                signals.append(signal)
                position = None
        
        self.signals = signals
        return signals
    
    def get_strategy_name(self) -> str:
        return f"Bollinger Bands Strategy (period={self.bb_period}, std={self.bb_std})"