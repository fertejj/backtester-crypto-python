import time
import hmac
import hashlib
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.settings import settings


class BingXClient:
    """Cliente para la API de BingX"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, use_synthetic: bool = False):
        self.api_key = api_key or settings.bingx_api_key
        self.secret_key = secret_key or settings.bingx_secret_key
        self.base_url = settings.bingx_base_url
        self.use_synthetic = use_synthetic
        
        # Si no hay credenciales válidas, usar datos sintéticos
        if not self.api_key or not self.secret_key or self.api_key == "demo":
            print("⚠️  Sin credenciales API válidas - usando datos sintéticos")
            self.use_synthetic = True
    
    def _generate_signature(self, query_string: str) -> str:
        """Genera la firma HMAC SHA256 para la API"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, 
                     signed: bool = False) -> Dict[str, Any]:
        """Realiza una petición HTTP a la API"""
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        if signed:
            timestamp = int(time.time() * 1000)
            params['timestamp'] = timestamp
            
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            signature = self._generate_signature(query_string)
            
            headers = {
                'X-BX-APIKEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            params['signature'] = signature
        else:
            headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error en petición API: {e}")
    
    def get_klines(self, symbol: str, interval: str, limit: int = 1000, 
                   start_time: Optional[int] = None, end_time: Optional[int] = None) -> pd.DataFrame:
        """
        Obtiene datos de velas (klines) históricos
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            interval: Intervalo de tiempo (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Número máximo de velas (max 1000)
            start_time: Timestamp de inicio en millisegundos
            end_time: Timestamp de fin en millisegundos
        """
        endpoint = "/openApi/swap/v3/quote/klines"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        
        response = self._make_request(endpoint, params)
        
        if response.get('code') != 0:
            raise Exception(f"Error API: {response.get('msg', 'Error desconocido')}")
        
        data = response.get('data', [])
        
        if not data:
            return pd.DataFrame()
        
        # Convertir a DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_volume', 'count', 'taker_buy_volume', 
            'taker_buy_quote_volume', 'ignore'
        ])
        
        # Convertir tipos de datos
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_columns] = df[numeric_columns].astype(float)
        
        # Convertir timestamp a datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('datetime', inplace=True)
        
        return df[['open', 'high', 'low', 'close', 'volume']]
    
    def get_symbols(self) -> List[Dict[str, Any]]:
        """Obtiene lista de símbolos disponibles"""
        endpoint = "/openApi/swap/v2/quote/contracts"
        
        response = self._make_request(endpoint)
        
        if response.get('code') != 0:
            raise Exception(f"Error API: {response.get('msg', 'Error desconocido')}")
        
        return response.get('data', [])
    
    def get_historical_data(self, symbol: str, interval: str, 
                           start_date: str, end_date: str) -> pd.DataFrame:
        """
        Obtiene datos históricos para un rango de fechas
        
        Args:
            symbol: Par de trading
            interval: Intervalo de tiempo
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
        """
        # Si está configurado para usar datos sintéticos
        if self.use_synthetic:
            print("📊 Usando datos sintéticos para demo...")
            return self._generate_synthetic_data(symbol, interval, start_date, end_date)
        
        try:
            print(f"📡 Obteniendo datos reales de {symbol} desde BingX API...")
            return self._fetch_real_data(symbol, interval, start_date, end_date)
        
        except Exception as e:
            print(f"❌ Error obteniendo datos de la API: {e}")
            print("🔄 Fallback a datos sintéticos...")
            return self._generate_synthetic_data(symbol, interval, start_date, end_date)
    
    def _fetch_real_data(self, symbol: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Obtiene datos reales usando el método existente"""
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_timestamp = int(start_dt.timestamp() * 1000)
        end_timestamp = int(end_dt.timestamp() * 1000)
        
        all_data = []
        current_start = start_timestamp
        
        # Obtener datos en chunks debido al límite de 1000 velas
        while current_start < end_timestamp:
            df_chunk = self.get_klines(
                symbol=symbol,
                interval=interval,
                limit=1000,
                start_time=current_start,
                end_time=end_timestamp
            )
            
            if df_chunk.empty:
                break
            
            all_data.append(df_chunk)
            
            # Actualizar el timestamp de inicio para el próximo chunk
            last_timestamp = int(df_chunk.index[-1].timestamp() * 1000)
            current_start = last_timestamp + 1
            
            # Pequeña pausa para evitar rate limiting
            time.sleep(0.1)
        
        if not all_data:
            raise ValueError(f"No se pudieron obtener datos para {symbol}")
        
        # Combinar todos los chunks
        df = pd.concat(all_data).drop_duplicates()
        df.sort_index(inplace=True)
        
        print(f"✅ Obtenidos {len(df)} registros reales de {symbol}")
        return df
    
    def _generate_synthetic_data(self, symbol: str, interval: str, 
                               start_date: str, end_date: str) -> pd.DataFrame:
        """
        Obtiene datos históricos para un rango de fechas
        
        Args:
            symbol: Par de trading
            interval: Intervalo de tiempo
            start_date: Fecha inicio (YYYY-MM-DD)
            end_date: Fecha fin (YYYY-MM-DD)
        """
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_timestamp = int(start_dt.timestamp() * 1000)
        end_timestamp = int(end_dt.timestamp() * 1000)
        
        all_data = []
        current_start = start_timestamp
        
        # Obtener datos en chunks debido al límite de 1000 velas
        while current_start < end_timestamp:
            df_chunk = self.get_klines(
                symbol=symbol,
                interval=interval,
                limit=1000,
                start_time=current_start,
                end_time=end_timestamp
            )
            
            if df_chunk.empty:
                break
            
            all_data.append(df_chunk)
            
            # Actualizar el timestamp de inicio para el próximo chunk
            last_timestamp = int(df_chunk.index[-1].timestamp() * 1000)
            current_start = last_timestamp + 1
            
            # Pequeña pausa para evitar rate limiting
            time.sleep(0.1)
        
        if not all_data:
            return pd.DataFrame()
        
        # Combinar todos los chunks
        df = pd.concat(all_data).drop_duplicates()
        df.sort_index(inplace=True)
        
        return df
    
    def _generate_synthetic_data(self, symbol: str, interval: str, 
                               start_date: str, end_date: str) -> pd.DataFrame:
        """
        Genera datos sintéticos para pruebas cuando no hay API disponible
        """
        print(f"🎲 Generando datos sintéticos para {symbol} ({interval})")
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Mapeo de intervalos a frecuencias
        freq_map = {
            '1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min',
            '1h': '1h', '4h': '4h', '1d': '1D', '1w': '1W'
        }
        
        freq = freq_map.get(interval, '1h')
        
        # Generar índice de fechas
        date_range = pd.date_range(start=start_dt, end=end_dt, freq=freq)
        
        if len(date_range) < 2:
            # Asegurar al menos algunos datos
            date_range = pd.date_range(start=start_dt, periods=100, freq=freq)
        
        # Precio inicial basado en el símbolo
        if 'BTC' in symbol.upper():
            base_price = 43000
        elif 'ETH' in symbol.upper():
            base_price = 2500
        elif 'BNB' in symbol.upper():
            base_price = 320
        else:
            base_price = 1.0
        
        np.random.seed(42)  # Para resultados reproducibles
        
        # Generar datos OHLC sintéticos
        data = []
        current_price = base_price
        
        for i, timestamp in enumerate(date_range):
            # Tendencia ligeramente alcista con volatilidad
            trend = np.random.normal(0.0002, 0.02)  # 0.02% tendencia, 2% volatilidad
            current_price *= (1 + trend)
            
            # Generar OHLC basado en el precio actual
            volatility = abs(np.random.normal(0, 0.015))  # 1.5% volatilidad intraday
            
            open_price = current_price
            high_price = open_price * (1 + volatility)
            low_price = open_price * (1 - volatility)
            
            # Close price con tendencia
            close_trend = np.random.normal(0, 0.008)  # 0.8% movimiento del close
            close_price = open_price * (1 + close_trend)
            
            # Asegurar que high >= max(open, close) y low <= min(open, close)
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Volumen sintético
            volume = np.random.exponential(1000) + 500  # Volumen exponencial
            
            data.append({
                'open': round(open_price, 4),
                'high': round(high_price, 4),
                'low': round(low_price, 4),
                'close': round(close_price, 4),
                'volume': round(volume, 2)
            })
            
            current_price = close_price
        
        # Crear DataFrame
        df = pd.DataFrame(data, index=date_range)
        
        print(f"✅ Generados {len(df)} registros sintéticos de {symbol}")
        return df