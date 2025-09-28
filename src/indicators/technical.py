import pandas as pd
import numpy as np
import ta


class TechnicalIndicators:
    """Clase para calcular indicadores técnicos"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        return ta.momentum.rsi(data, window=period)
    
    @staticmethod
    def macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, 
             signal_period: int = 9) -> pd.DataFrame:
        """MACD (Moving Average Convergence Divergence)"""
        macd_line = ta.trend.macd(data, window_slow=slow_period, window_fast=fast_period)
        macd_signal = ta.trend.macd_signal(data, window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
        macd_histogram = ta.trend.macd_diff(data, window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
        
        return pd.DataFrame({
            'macd': macd_line,
            'signal': macd_signal,
            'histogram': macd_histogram
        }, index=data.index)
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std: float = 2) -> pd.DataFrame:
        """Bollinger Bands"""
        bb_high = ta.volatility.bollinger_hband(data, window=period, window_dev=std)
        bb_mid = ta.volatility.bollinger_mavg(data, window=period)
        bb_low = ta.volatility.bollinger_lband(data, window=period, window_dev=std)
        
        return pd.DataFrame({
            'upper': bb_high,
            'middle': bb_mid,
            'lower': bb_low
        }, index=data.index)
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                   k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """Stochastic Oscillator"""
        k_percent = ta.momentum.stoch(high, low, close, window=k_period, smooth_window=d_period)
        d_percent = ta.momentum.stoch_signal(high, low, close, window=k_period, smooth_window=d_period)
        
        return pd.DataFrame({
            'k_percent': k_percent,
            'd_percent': d_percent
        }, index=close.index)
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        return ta.volatility.average_true_range(high, low, close, window=period)
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average Directional Index"""
        return ta.trend.adx(high, low, close, window=period)
    
    @staticmethod
    def cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """Commodity Channel Index"""
        return ta.trend.cci(high, low, close, window=period)
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Williams %R"""
        return ta.momentum.williams_r(high, low, close, lbp=period)
    
    @staticmethod
    def volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
        """Volume Simple Moving Average"""
        return volume.rolling(window=period).mean()
    
    @classmethod
    def add_all_indicators(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega todos los indicadores técnicos al DataFrame"""
        df = df.copy()
        
        # Moving averages
        df['sma_20'] = cls.sma(df['close'], 20)
        df['sma_50'] = cls.sma(df['close'], 50)
        df['ema_12'] = cls.ema(df['close'], 12)
        df['ema_26'] = cls.ema(df['close'], 26)
        
        # RSI
        df['rsi'] = cls.rsi(df['close'])
        
        # MACD
        macd_data = cls.macd(df['close'])
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_histogram'] = macd_data['histogram']
        
        # Bollinger Bands
        bb_data = cls.bollinger_bands(df['close'])
        df['bb_upper'] = bb_data['upper']
        df['bb_middle'] = bb_data['middle']
        df['bb_lower'] = bb_data['lower']
        
        # Stochastic
        stoch_data = cls.stochastic(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch_data['k_percent']
        df['stoch_d'] = stoch_data['d_percent']
        
        # ATR
        df['atr'] = cls.atr(df['high'], df['low'], df['close'])
        
        # ADX
        df['adx'] = cls.adx(df['high'], df['low'], df['close'])
        
        # Volume indicators
        df['volume_sma'] = cls.volume_sma(df['volume'])
        
        return df