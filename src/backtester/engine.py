import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from src.api.bingx_client import BingXClient
from src.strategies.base import BaseStrategy, SignalType, TradeSignal
from src.backtester.metrics import BacktestResults, PerformanceMetrics, Trade
from src.risk.manager import RiskManager, RiskParameters
from src.indicators.technical import TechnicalIndicators


class BacktesterEngine:
    """Motor principal de backtesting"""
    
    def __init__(self, api_client: Optional[BingXClient] = None, 
                 commission: float = 0.001, slippage: float = 0.001):
        self.api_client = api_client
        self.commission = commission  # Comisión por operación (0.1%)
        self.slippage = slippage      # Slippage (0.1%)
        
    def run_backtest(self, strategy: BaseStrategy, start_date: str, end_date: str,
                    initial_capital: float = 10000, interval: str = "1h",
                    risk_params: Optional[RiskParameters] = None) -> BacktestResults:
        """
        Ejecuta un backtest completo
        
        Args:
            strategy: Estrategia a testear
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
            initial_capital: Capital inicial
            interval: Intervalo de tiempo (1m, 5m, 15m, 1h, 4h, 1d)
            risk_params: Parámetros de gestión de riesgo
            
        Returns:
            Resultados del backtest
        """
        print(f"Iniciando backtest de {strategy.get_strategy_name()}")
        print(f"Período: {start_date} a {end_date}")
        print(f"Capital inicial: ${initial_capital:,.2f}")
        
        # Obtener datos históricos
        data = self._get_historical_data(strategy.symbol, interval, start_date, end_date)
        
        if data.empty:
            raise ValueError("No se pudieron obtener datos históricos")
        
        # Agregar indicadores técnicos
        data = TechnicalIndicators.add_all_indicators(data)
        
        # Generar señales
        print("Generando señales de trading...")
        signals = strategy.generate_signals(data)
        
        if not signals:
            print("No se generaron señales de trading")
            return BacktestResults(
                initial_capital=initial_capital,
                final_capital=initial_capital,
                total_return=0.0,
                total_return_pct=0.0
            )
        
        print(f"Señales generadas: {len(signals)}")
        
        # Configurar gestión de riesgo
        if risk_params is None:
            risk_params = RiskParameters()
        risk_manager = RiskManager(risk_params)
        
        # Ejecutar simulación
        return self._simulate_trading(data, signals, initial_capital, risk_manager)
    
    def _get_historical_data(self, symbol: str, interval: str, 
                           start_date: str, end_date: str) -> pd.DataFrame:
        """Obtiene datos históricos de la API o genera datos sintéticos"""
        if self.api_client:
            try:
                return self.api_client.get_historical_data(symbol, interval, start_date, end_date)
            except Exception as e:
                print(f"Error obteniendo datos de API: {e}")
                print("Generando datos sintéticos para demo...")
                return self._generate_synthetic_data(symbol, start_date, end_date, interval)
        else:
            print("No hay cliente API configurado. Generando datos sintéticos...")
            return self._generate_synthetic_data(symbol, start_date, end_date, interval)
    
    def _generate_synthetic_data(self, symbol: str, start_date: str, 
                               end_date: str, interval: str = "1h") -> pd.DataFrame:
        """Genera datos sintéticos para testing"""
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Determinar frecuencia basada en el intervalo
        freq_map = {
            '1m': '1T', '5m': '5T', '15m': '15T', '30m': '30T',
            '1h': '1H', '2h': '2H', '4h': '4H', '6h': '6H', '12h': '12H',
            '1d': '1D', '1w': '1W'
        }
        
        freq = freq_map.get(interval, '1H')
        date_range = pd.date_range(start=start_dt, end=end_dt, freq=freq)
        
        # Generar precios usando random walk con tendencia
        np.random.seed(42)  # Para resultados reproducibles
        n_periods = len(date_range)
        
        # Precio inicial
        initial_price = 50000 if 'BTC' in symbol else 3000 if 'ETH' in symbol else 1.0
        
        # Generar retornos aleatorios
        daily_vol = 0.02  # 2% volatilidad diaria
        returns = np.random.normal(0.0005, daily_vol, n_periods)  # Ligera tendencia alcista
        
        # Generar precios
        prices = [initial_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 0.01))  # Evitar precios negativos
        
        # Generar OHLC
        data = []
        for i in range(n_periods):
            if i == 0:
                open_price = prices[i]
            else:
                open_price = data[i-1]['close']  # Close anterior
            
            close_price = prices[i]
            
            # High y Low basados en volatilidad intraperiodo
            intraday_vol = daily_vol * 0.5
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, intraday_vol)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, intraday_vol)))
            
            # Volumen aleatorio
            base_volume = 1000000
            volume = base_volume * (0.5 + np.random.random())
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })
        
        df = pd.DataFrame(data, index=date_range)
        return df
    
    def _simulate_trading(self, data: pd.DataFrame, signals: List[TradeSignal],
                         initial_capital: float, risk_manager: RiskManager) -> BacktestResults:
        """Simula el trading basado en las señales"""
        print("Simulando operaciones...")
        
        capital = initial_capital
        equity_curve = []
        trades = []
        current_trade: Optional[Trade] = None
        
        # Indexar señales por timestamp para búsqueda eficiente
        signal_dict = {signal.timestamp: signal for signal in signals}
        
        for timestamp, row in data.iterrows():
            current_price = row['close']
            
            # Verificar si hay señal en este timestamp
            if timestamp in signal_dict:
                signal = signal_dict[timestamp]
                
                if signal.signal_type == SignalType.BUY and current_trade is None:
                    # Abrir posición larga
                    if risk_manager.should_enter_trade(initial_capital, capital):
                        # Calcular stop loss y take profit
                        stop_loss = risk_manager.calculate_stop_loss(current_price, "long")
                        take_profit = risk_manager.calculate_take_profit(current_price, "long")
                        
                        # Calcular tamaño de posición
                        position_size = risk_manager.calculate_position_size(
                            capital, current_price, stop_loss
                        )
                        
                        if position_size > 0:
                            # Aplicar slippage
                            entry_price = current_price * (1 + self.slippage)
                            
                            # Calcular comisión
                            position_value = position_size * entry_price
                            commission = position_value * self.commission
                            
                            # Crear trade
                            current_trade = Trade(
                                entry_time=timestamp,
                                entry_price=entry_price,
                                quantity=position_size,
                                side="long",
                                commission=commission
                            )
                            
                            # Actualizar capital
                            capital -= commission
                
                elif signal.signal_type == SignalType.SELL and current_trade is not None:
                    # Cerrar posición
                    exit_price = current_price * (1 - self.slippage)
                    exit_commission = current_trade.quantity * exit_price * self.commission
                    
                    # Calcular PnL
                    gross_pnl = current_trade.quantity * (exit_price - current_trade.entry_price)
                    net_pnl = gross_pnl - current_trade.commission - exit_commission
                    pnl_pct = net_pnl / (current_trade.quantity * current_trade.entry_price)
                    
                    # Completar trade
                    current_trade.exit_time = timestamp
                    current_trade.exit_price = exit_price
                    current_trade.pnl = net_pnl
                    current_trade.pnl_pct = pnl_pct
                    current_trade.commission += exit_commission
                    current_trade.is_open = False
                    
                    # Actualizar capital
                    capital += net_pnl - exit_commission
                    
                    # Agregar trade a la lista
                    trades.append(current_trade)
                    current_trade = None
                    
                    # Actualizar risk manager
                    risk_manager.update_daily_pnl(net_pnl)
            
            # Verificar stop loss y take profit para trade abierto
            if current_trade is not None:
                should_exit, reason = risk_manager.should_exit_trade(
                    current_price, current_trade.entry_price, current_trade.side,
                    signal.stop_loss if timestamp in signal_dict else None,
                    signal.take_profit if timestamp in signal_dict else None
                )
                
                if should_exit:
                    # Cerrar por stop loss o take profit
                    exit_price = current_price * (1 - self.slippage)
                    exit_commission = current_trade.quantity * exit_price * self.commission
                    
                    gross_pnl = current_trade.quantity * (exit_price - current_trade.entry_price)
                    net_pnl = gross_pnl - current_trade.commission - exit_commission
                    pnl_pct = net_pnl / (current_trade.quantity * current_trade.entry_price)
                    
                    current_trade.exit_time = timestamp
                    current_trade.exit_price = exit_price
                    current_trade.pnl = net_pnl
                    current_trade.pnl_pct = pnl_pct
                    current_trade.commission += exit_commission
                    current_trade.is_open = False
                    
                    capital += net_pnl - exit_commission
                    trades.append(current_trade)
                    current_trade = None
                    
                    risk_manager.update_daily_pnl(net_pnl)
            
            # Guardar equity para curva
            current_equity = capital
            if current_trade is not None:
                # Agregar PnL no realizado
                unrealized_pnl = current_trade.quantity * (current_price - current_trade.entry_price)
                current_equity += unrealized_pnl
            
            equity_curve.append(current_equity)
        
        # Cerrar trade abierto al final
        if current_trade is not None:
            final_price = data.iloc[-1]['close']
            exit_price = final_price * (1 - self.slippage)
            exit_commission = current_trade.quantity * exit_price * self.commission
            
            gross_pnl = current_trade.quantity * (exit_price - current_trade.entry_price)
            net_pnl = gross_pnl - current_trade.commission - exit_commission
            pnl_pct = net_pnl / (current_trade.quantity * current_trade.entry_price)
            
            current_trade.exit_time = data.index[-1]
            current_trade.exit_price = exit_price
            current_trade.pnl = net_pnl
            current_trade.pnl_pct = pnl_pct
            current_trade.commission += exit_commission
            current_trade.is_open = False
            
            trades.append(current_trade)
            capital += net_pnl - exit_commission
        
        # Crear serie temporal de equity
        equity_series = pd.Series(equity_curve, index=data.index)
        
        # Calcular métricas
        results = PerformanceMetrics.calculate_all_metrics(
            initial_capital, equity_series, trades
        )
        
        print(f"Backtest completado. Trades ejecutados: {len(trades)}")
        return results