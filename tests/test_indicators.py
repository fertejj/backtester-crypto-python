import pytest
import pandas as pd
import numpy as np
from src.indicators.technical import TechnicalIndicators


class TestTechnicalIndicators:
    """Tests para indicadores técnicos"""
    
    @pytest.fixture
    def sample_data(self):
        """Datos de ejemplo para testing"""
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='1H')
        
        # Generar precios sintéticos
        prices = [100]
        for _ in range(99):
            change = np.random.normal(0, 0.02)
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1))
        
        data = pd.DataFrame({
            'close': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'volume': [1000 + np.random.randint(0, 5000) for _ in prices]
        }, index=dates)
        
        data['open'] = data['close'].shift(1).fillna(data['close'].iloc[0])
        return data
    
    def test_sma(self, sample_data):
        """Test Simple Moving Average"""
        sma_20 = TechnicalIndicators.sma(sample_data['close'], 20)
        
        assert len(sma_20) == len(sample_data)
        assert pd.isna(sma_20.iloc[:19]).all()  # Primeros 19 valores deben ser NaN
        assert not pd.isna(sma_20.iloc[19:]).any()  # Resto no debe ser NaN
        
        # Verificar cálculo manual para un punto
        manual_sma = sample_data['close'].iloc[0:20].mean()
        assert abs(sma_20.iloc[19] - manual_sma) < 1e-10
    
    def test_ema(self, sample_data):
        """Test Exponential Moving Average"""
        ema_12 = TechnicalIndicators.ema(sample_data['close'], 12)
        
        assert len(ema_12) == len(sample_data)
        assert not pd.isna(ema_12).all()  # No todos deben ser NaN
    
    def test_rsi(self, sample_data):
        """Test Relative Strength Index"""
        rsi = TechnicalIndicators.rsi(sample_data['close'], 14)
        
        assert len(rsi) == len(sample_data)
        
        # RSI debe estar entre 0 y 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_macd(self, sample_data):
        """Test MACD"""
        macd_data = TechnicalIndicators.macd(sample_data['close'])
        
        assert 'macd' in macd_data.columns
        assert 'signal' in macd_data.columns
        assert 'histogram' in macd_data.columns
        
        assert len(macd_data) == len(sample_data)
    
    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands"""
        bb_data = TechnicalIndicators.bollinger_bands(sample_data['close'], 20, 2)
        
        assert 'upper' in bb_data.columns
        assert 'middle' in bb_data.columns
        assert 'lower' in bb_data.columns
        
        # Verificar que upper > middle > lower (donde no hay NaN)
        valid_data = bb_data.dropna()
        assert (valid_data['upper'] >= valid_data['middle']).all()
        assert (valid_data['middle'] >= valid_data['lower']).all()
    
    def test_stochastic(self, sample_data):
        """Test Stochastic Oscillator"""
        stoch_data = TechnicalIndicators.stochastic(
            sample_data['high'], 
            sample_data['low'], 
            sample_data['close']
        )
        
        assert 'k_percent' in stoch_data.columns
        assert 'd_percent' in stoch_data.columns
        
        # Valores deben estar entre 0 y 100
        valid_k = stoch_data['k_percent'].dropna()
        valid_d = stoch_data['d_percent'].dropna()
        
        assert (valid_k >= 0).all() and (valid_k <= 100).all()
        assert (valid_d >= 0).all() and (valid_d <= 100).all()
    
    def test_atr(self, sample_data):
        """Test Average True Range"""
        atr = TechnicalIndicators.atr(
            sample_data['high'], 
            sample_data['low'], 
            sample_data['close']
        )
        
        assert len(atr) == len(sample_data)
        
        # ATR debe ser siempre positivo
        valid_atr = atr.dropna()
        assert (valid_atr >= 0).all()
    
    def test_add_all_indicators(self, sample_data):
        """Test agregar todos los indicadores"""
        df_with_indicators = TechnicalIndicators.add_all_indicators(sample_data)
        
        expected_indicators = [
            'sma_20', 'sma_50', 'ema_12', 'ema_26', 'rsi',
            'macd', 'macd_signal', 'macd_histogram',
            'bb_upper', 'bb_middle', 'bb_lower',
            'stoch_k', 'stoch_d', 'atr', 'adx', 'volume_sma'
        ]
        
        for indicator in expected_indicators:
            assert indicator in df_with_indicators.columns
        
        # Verificar que el DataFrame original no se modificó
        original_columns = set(sample_data.columns)
        assert original_columns.issubset(set(df_with_indicators.columns))