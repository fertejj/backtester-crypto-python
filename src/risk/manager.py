from typing import Optional
from dataclasses import dataclass


@dataclass
class RiskParameters:
    """Parámetros de gestión de riesgo"""
    max_position_size: float = 0.1  # 10% del capital por posición
    stop_loss_pct: Optional[float] = None  # Stop loss porcentual
    take_profit_pct: Optional[float] = None  # Take profit porcentual
    max_daily_loss: Optional[float] = None  # Pérdida máxima diaria
    max_drawdown: Optional[float] = None  # Drawdown máximo permitido
    risk_per_trade: float = 0.02  # 2% de riesgo por operación


class RiskManager:
    """Gestor de riesgo para backtesting"""
    
    def __init__(self, parameters: RiskParameters):
        self.parameters = parameters
        self.daily_pnl = 0.0
        self.current_drawdown = 0.0
        
    def calculate_position_size(self, capital: float, price: float, 
                              stop_loss_price: Optional[float] = None) -> float:
        """
        Calcula el tamaño de posición basado en los parámetros de riesgo
        
        Args:
            capital: Capital disponible
            price: Precio de entrada
            stop_loss_price: Precio de stop loss
            
        Returns:
            Tamaño de posición en unidades base
        """
        # Tamaño máximo basado en porcentaje del capital
        max_position_value = capital * self.parameters.max_position_size
        max_position_size = max_position_value / price
        
        # Si hay stop loss, ajustar tamaño basado en riesgo por operación
        if stop_loss_price is not None:
            risk_per_unit = abs(price - stop_loss_price)
            risk_capital = capital * self.parameters.risk_per_trade
            risk_based_size = risk_capital / risk_per_unit
            
            # Usar el menor de los dos
            position_size = min(max_position_size, risk_based_size)
        else:
            position_size = max_position_size
        
        return max(0, position_size)
    
    def should_enter_trade(self, capital: float, current_equity: float) -> bool:
        """
        Determina si se debe entrar en una nueva operación
        
        Args:
            capital: Capital inicial
            current_equity: Equity actual
            
        Returns:
            True si se puede entrar en la operación
        """
        # Verificar pérdida máxima diaria
        if (self.parameters.max_daily_loss is not None and 
            self.daily_pnl < -self.parameters.max_daily_loss):
            return False
        
        # Verificar drawdown máximo
        if self.parameters.max_drawdown is not None:
            current_dd = (capital - current_equity) / capital
            if current_dd > self.parameters.max_drawdown:
                return False
        
        return True
    
    def calculate_stop_loss(self, entry_price: float, side: str = "long") -> Optional[float]:
        """
        Calcula el precio de stop loss
        
        Args:
            entry_price: Precio de entrada
            side: Lado de la operación ("long" o "short")
            
        Returns:
            Precio de stop loss o None si no se usa
        """
        if self.parameters.stop_loss_pct is None:
            return None
        
        if side == "long":
            return entry_price * (1 - self.parameters.stop_loss_pct)
        else:  # short
            return entry_price * (1 + self.parameters.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, side: str = "long") -> Optional[float]:
        """
        Calcula el precio de take profit
        
        Args:
            entry_price: Precio de entrada
            side: Lado de la operación ("long" o "short")
            
        Returns:
            Precio de take profit o None si no se usa
        """
        if self.parameters.take_profit_pct is None:
            return None
        
        if side == "long":
            return entry_price * (1 + self.parameters.take_profit_pct)
        else:  # short
            return entry_price * (1 - self.parameters.take_profit_pct)
    
    def should_exit_trade(self, current_price: float, entry_price: float, 
                         side: str = "long", stop_loss: Optional[float] = None,
                         take_profit: Optional[float] = None) -> tuple:
        """
        Determina si se debe cerrar una operación por stop loss o take profit
        
        Args:
            current_price: Precio actual
            entry_price: Precio de entrada
            side: Lado de la operación
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
            
        Returns:
            (should_exit, reason)
        """
        if side == "long":
            # Stop loss para posición larga
            if stop_loss is not None and current_price <= stop_loss:
                return True, "stop_loss"
            
            # Take profit para posición larga
            if take_profit is not None and current_price >= take_profit:
                return True, "take_profit"
        
        else:  # short
            # Stop loss para posición corta
            if stop_loss is not None and current_price >= stop_loss:
                return True, "stop_loss"
            
            # Take profit para posición corta
            if take_profit is not None and current_price <= take_profit:
                return True, "take_profit"
        
        return False, ""
    
    def update_daily_pnl(self, pnl: float):
        """Actualiza el PnL diario"""
        self.daily_pnl += pnl
    
    def reset_daily_pnl(self):
        """Resetea el PnL diario (llamar al final de cada día)"""
        self.daily_pnl = 0.0