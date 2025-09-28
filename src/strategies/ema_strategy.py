import pandas as pd
import numpy as np
from typing import List
from .base import BaseStrategy, TradeSignal, SignalType
from src.indicators.technical import TechnicalIndicators


class EMAStrategy(BaseStrategy):
    """
    Estrategia basada en 3 EMAs (20, 55, 200) con filtros direccionales
    
    Lógica de Trading:
    - EMA 20: Señal de entrada rápida
    - EMA 55: Confirmación de tendencia media
    - EMA 200: Filtro de tendencia principal
    
    Señales LONG:
    - EMA 20 > EMA 55 > EMA 200 (tendencia alcista)
    - Precio cruza por encima de EMA 20
    - Confirmación: EMA 20 pendiente positiva
    
    Señales SHORT:
    - EMA 20 < EMA 55 < EMA 200 (tendencia bajista)
    - Precio cruza por debajo de EMA 20
    - Confirmación: EMA 20 pendiente negativa
    """
    
    def __init__(self, symbol: str, fast_ema: int = 20, medium_ema: int = 55, 
                 slow_ema: int = 200, min_trend_strength: float = 0.001,
                 allow_longs: bool = True, allow_shorts: bool = False,
                 trend_filter: bool = True, **kwargs):
        super().__init__(symbol, **kwargs)
        self.fast_ema = fast_ema
        self.medium_ema = medium_ema
        self.slow_ema = slow_ema
        self.min_trend_strength = min_trend_strength  # Mínima pendiente para confirmar tendencia
        self.allow_longs = allow_longs
        self.allow_shorts = allow_shorts
        self.trend_filter = trend_filter  # Si usar EMA 200 como filtro
        
    def generate_signals(self, data: pd.DataFrame) -> List[TradeSignal]:
        """Genera señales basadas en EMAs múltiples"""
        if not self.validate_data(data):
            raise ValueError("Datos inválidos: faltan columnas OHLCV")
        
        # Calcular EMAs
        data['ema_fast'] = TechnicalIndicators.ema(data['close'], self.fast_ema)
        data['ema_medium'] = TechnicalIndicators.ema(data['close'], self.medium_ema)
        data['ema_slow'] = TechnicalIndicators.ema(data['close'], self.slow_ema)
        
        # Calcular pendientes de EMAs (fuerza de tendencia)
        data['ema_fast_slope'] = data['ema_fast'].pct_change(5)  # Pendiente en 5 períodos
        data['ema_medium_slope'] = data['ema_medium'].pct_change(5)
        data['ema_slow_slope'] = data['ema_slow'].pct_change(10)  # Pendiente más lenta
        
        signals = []
        position = None  # None, 'long', 'short'
        
        for i in range(max(self.slow_ema, 10), len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            # Verificar que tenemos todos los datos
            if (pd.isna(current['ema_fast']) or pd.isna(current['ema_medium']) or 
                pd.isna(current['ema_slow'])):
                continue
            
            timestamp = data.index[i]
            current_price = current['close']
            
            # Evaluar condiciones de tendencia
            bullish_alignment = (current['ema_fast'] > current['ema_medium'] > current['ema_slow'])
            bearish_alignment = (current['ema_fast'] < current['ema_medium'] < current['ema_slow'])
            
            # Evaluar fuerza de tendencia
            strong_bullish_trend = (current['ema_fast_slope'] > self.min_trend_strength and
                                   current['ema_medium_slope'] > 0)
            strong_bearish_trend = (current['ema_fast_slope'] < -self.min_trend_strength and
                                   current['ema_medium_slope'] < 0)
            
            # Detectar cruces de precio con EMA rápida
            price_cross_above_fast = (previous['close'] <= previous['ema_fast'] and 
                                     current_price > current['ema_fast'])
            price_cross_below_fast = (previous['close'] >= previous['ema_fast'] and 
                                     current_price < current['ema_fast'])
            
            # SEÑALES LONG
            if (self.allow_longs and position != 'long' and price_cross_above_fast):
                # Condiciones para entrada LONG
                trend_ok = True
                if self.trend_filter:
                    trend_ok = bullish_alignment
                
                if trend_ok and strong_bullish_trend:
                    # Calcular confianza basada en alineación y fuerza de tendencia
                    alignment_score = 0.6 if bullish_alignment else 0.3
                    strength_score = min(current['ema_fast_slope'] / self.min_trend_strength * 0.4, 0.4)
                    confidence = min(alignment_score + strength_score, 1.0)
                    
                    signal = TradeSignal(
                        timestamp=timestamp,
                        signal_type=SignalType.BUY,
                        price=current_price,
                        confidence=confidence,
                        reason=f"EMA bullish cross: Fast>{self.fast_ema:.2f}, Med>{self.medium_ema:.2f}, Slow>{self.slow_ema:.2f}"
                    )
                    signals.append(signal)
                    position = 'long'
            
            # SEÑALES SHORT
            elif (self.allow_shorts and position != 'short' and price_cross_below_fast):
                # Condiciones para entrada SHORT
                trend_ok = True
                if self.trend_filter:
                    trend_ok = bearish_alignment
                
                if trend_ok and strong_bearish_trend:
                    # Calcular confianza
                    alignment_score = 0.6 if bearish_alignment else 0.3
                    strength_score = min(abs(current['ema_fast_slope']) / self.min_trend_strength * 0.4, 0.4)
                    confidence = min(alignment_score + strength_score, 1.0)
                    
                    signal = TradeSignal(
                        timestamp=timestamp,
                        signal_type=SignalType.SELL,
                        price=current_price,
                        confidence=confidence,
                        reason=f"EMA bearish cross: Fast<{self.fast_ema:.2f}, Med<{self.medium_ema:.2f}, Slow<{self.slow_ema:.2f}"
                    )
                    signals.append(signal)
                    position = 'short'
            
            # SALIDAS
            elif position == 'long':
                # Salida LONG: precio cruza por debajo de EMA media o cambio de tendencia
                exit_condition = (price_cross_below_fast and current['ema_fast_slope'] < 0) or \
                               (self.trend_filter and not bullish_alignment and current['ema_fast'] < current['ema_medium'])
                
                if exit_condition:
                    signal = TradeSignal(
                        timestamp=timestamp,
                        signal_type=SignalType.SELL,
                        price=current_price,
                        confidence=0.8,
                        reason="EMA trend reversal - Exit LONG"
                    )
                    signals.append(signal)
                    position = None
            
            elif position == 'short':
                # Salida SHORT: precio cruza por encima de EMA media o cambio de tendencia
                exit_condition = (price_cross_above_fast and current['ema_fast_slope'] > 0) or \
                               (self.trend_filter and not bearish_alignment and current['ema_fast'] > current['ema_medium'])
                
                if exit_condition:
                    signal = TradeSignal(
                        timestamp=timestamp,
                        signal_type=SignalType.SELL,
                        price=current_price,
                        confidence=0.8,
                        reason="EMA trend reversal - Exit SHORT"
                    )
                    signals.append(signal)
                    position = None
        
        self.signals = signals
        return signals
    
    def get_strategy_name(self) -> str:
        direction = "Long+Short" if (self.allow_longs and self.allow_shorts) else \
                   "Long Only" if self.allow_longs else "Short Only"
        filter_text = "w/Filter" if self.trend_filter else "No Filter"
        return f"EMA Strategy ({self.fast_ema},{self.medium_ema},{self.slow_ema}) - {direction} {filter_text}"


class EMAGoldenCrossStrategy(BaseStrategy):
    """
    Estrategia EMA Golden/Death Cross simplificada
    
    Señales:
    - Golden Cross: EMA rápida cruza por encima de EMA lenta
    - Death Cross: EMA rápida cruza por debajo de EMA lenta
    """
    
    def __init__(self, symbol: str, fast_ema: int = 50, slow_ema: int = 200, **kwargs):
        super().__init__(symbol, **kwargs)
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        
    def generate_signals(self, data: pd.DataFrame) -> List[TradeSignal]:
        """Genera señales basadas en cruce de EMAs"""
        if not self.validate_data(data):
            raise ValueError("Datos inválidos: faltan columnas OHLCV")
        
        # Calcular EMAs
        data['ema_fast'] = TechnicalIndicators.ema(data['close'], self.fast_ema)
        data['ema_slow'] = TechnicalIndicators.ema(data['close'], self.slow_ema)
        
        signals = []
        position = None
        
        for i in range(1, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i-1]
            
            if pd.isna(current['ema_fast']) or pd.isna(current['ema_slow']):
                continue
            
            timestamp = data.index[i]
            current_price = current['close']
            
            # Golden Cross (EMA rápida cruza por encima de lenta)
            if (previous['ema_fast'] <= previous['ema_slow'] and 
                current['ema_fast'] > current['ema_slow'] and 
                position != 'long'):
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.BUY,
                    price=current_price,
                    confidence=0.8,
                    reason=f"Golden Cross: EMA{self.fast_ema} > EMA{self.slow_ema}"
                )
                signals.append(signal)
                position = 'long'
            
            # Death Cross (EMA rápida cruza por debajo de lenta)
            elif (previous['ema_fast'] >= previous['ema_slow'] and 
                  current['ema_fast'] < current['ema_slow'] and 
                  position == 'long'):
                
                signal = TradeSignal(
                    timestamp=timestamp,
                    signal_type=SignalType.SELL,
                    price=current_price,
                    confidence=0.8,
                    reason=f"Death Cross: EMA{self.fast_ema} < EMA{self.slow_ema}"
                )
                signals.append(signal)
                position = None
        
        self.signals = signals
        return signals
    
    def get_strategy_name(self) -> str:
        return f"EMA Golden Cross ({self.fast_ema}/{self.slow_ema})"