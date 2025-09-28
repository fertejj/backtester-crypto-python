import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np
from typing import List, Optional
from plotly.offline import plot

from src.backtester.metrics import BacktestResults, Trade
from src.strategies.base import TradeSignal, SignalType


class ChartGenerator:
    """Generador de gráficos para análisis de backtesting"""
    
    @staticmethod
    def plot_price_and_signals(data: pd.DataFrame, signals: List[TradeSignal], 
                             symbol: str, title: Optional[str] = None) -> go.Figure:
        """
        Gráfico de precios con señales de entrada y salida
        
        Args:
            data: DataFrame con datos OHLC
            signals: Lista de señales de trading
            symbol: Símbolo del activo
            title: Título personalizado del gráfico
        """
        if title is None:
            title = f"{symbol} - Precio y Señales de Trading"
        
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="Precio",
            increasing_line_color='green',
            decreasing_line_color='red'
        ))
        
        # Agregar señales
        buy_signals = [s for s in signals if s.signal_type == SignalType.BUY]
        sell_signals = [s for s in signals if s.signal_type == SignalType.SELL]
        
        if buy_signals:
            fig.add_trace(go.Scatter(
                x=[s.timestamp for s in buy_signals],
                y=[s.price for s in buy_signals],
                mode='markers',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='green'
                ),
                name='Señal Compra',
                hovertemplate='<b>Compra</b><br>Fecha: %{x}<br>Precio: $%{y:.2f}<extra></extra>'
            ))
        
        if sell_signals:
            fig.add_trace(go.Scatter(
                x=[s.timestamp for s in sell_signals],
                y=[s.price for s in sell_signals],
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='red'
                ),
                name='Señal Venta',
                hovertemplate='<b>Venta</b><br>Fecha: %{x}<br>Precio: $%{y:.2f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Fecha",
            yaxis_title="Precio ($)",
            template="plotly_white",
            height=600,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def plot_equity_curve(results: BacktestResults, title: Optional[str] = None) -> go.Figure:
        """
        Gráfico de curva de equity y drawdown
        
        Args:
            results: Resultados del backtest
            title: Título personalizado
        """
        if title is None:
            title = "Curva de Equity y Drawdown"
        
        # Crear subplots
        fig = sp.make_subplots(
            rows=2, cols=1,
            subplot_titles=('Equity Curve', 'Drawdown'),
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3]
        )
        
        # Curva de equity
        fig.add_trace(
            go.Scatter(
                x=results.equity_curve.index,
                y=results.equity_curve.values,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Línea de capital inicial
        fig.add_hline(
            y=results.initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Capital Inicial: ${results.initial_capital:,.0f}",
            row=1, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(
                x=results.drawdown_series.index,
                y=results.drawdown_series.values * 100,  # Convertir a porcentaje
                mode='lines',
                name='Drawdown %',
                line=dict(color='red', width=2),
                fill='tonexty'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=800,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Fecha", row=2, col=1)
        fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
        
        return fig
    
    @staticmethod
    def plot_trade_analysis(trades: List[Trade], title: Optional[str] = None) -> go.Figure:
        """
        Análisis de trades individuales
        
        Args:
            trades: Lista de trades ejecutados
            title: Título personalizado
        """
        if title is None:
            title = "Análisis de Trades"
        
        if not trades:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay trades para mostrar",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Filtrar trades cerrados
        closed_trades = [t for t in trades if not t.is_open and t.pnl is not None]
        
        if not closed_trades:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay trades cerrados para mostrar",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Crear subplots
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'PnL por Trade',
                'Distribución de PnL',
                'PnL Acumulado',
                'Duración de Trades'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. PnL por trade
        pnl_values = [t.pnl for t in closed_trades]
        colors = ['green' if pnl > 0 else 'red' for pnl in pnl_values]
        
        fig.add_trace(
            go.Bar(
                x=list(range(1, len(closed_trades) + 1)),
                y=pnl_values,
                marker_color=colors,
                name='PnL por Trade',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # 2. Histograma de PnL
        fig.add_trace(
            go.Histogram(
                x=pnl_values,
                nbinsx=20,
                name='Distribución PnL',
                showlegend=False,
                marker_color='lightblue',
                opacity=0.7
            ),
            row=1, col=2
        )
        
        # 3. PnL acumulado
        cumulative_pnl = np.cumsum(pnl_values)
        fig.add_trace(
            go.Scatter(
                x=list(range(1, len(closed_trades) + 1)),
                y=cumulative_pnl,
                mode='lines+markers',
                name='PnL Acumulado',
                line=dict(color='blue', width=2),
                showlegend=False
            ),
            row=2, col=1
        )
        
        # 4. Duración de trades (en horas)
        durations = []
        for trade in closed_trades:
            if trade.exit_time and trade.entry_time:
                duration = (trade.exit_time - trade.entry_time).total_seconds() / 3600
                durations.append(duration)
        
        if durations:
            fig.add_trace(
                go.Histogram(
                    x=durations,
                    nbinsx=15,
                    name='Duración (horas)',
                    showlegend=False,
                    marker_color='orange',
                    opacity=0.7
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=800
        )
        
        # Actualizar etiquetas de ejes
        fig.update_xaxes(title_text="Trade #", row=1, col=1)
        fig.update_yaxes(title_text="PnL ($)", row=1, col=1)
        
        fig.update_xaxes(title_text="PnL ($)", row=1, col=2)
        fig.update_yaxes(title_text="Frecuencia", row=1, col=2)
        
        fig.update_xaxes(title_text="Trade #", row=2, col=1)
        fig.update_yaxes(title_text="PnL Acumulado ($)", row=2, col=1)
        
        fig.update_xaxes(title_text="Duración (horas)", row=2, col=2)
        fig.update_yaxes(title_text="Frecuencia", row=2, col=2)
        
        return fig
    
    @staticmethod
    def plot_indicators(data: pd.DataFrame, indicators: List[str], 
                       symbol: str, title: Optional[str] = None) -> go.Figure:
        """
        Gráfico de indicadores técnicos
        
        Args:
            data: DataFrame con datos e indicadores
            indicators: Lista de nombres de indicadores a mostrar
            symbol: Símbolo del activo
            title: Título personalizado
        """
        if title is None:
            title = f"{symbol} - Indicadores Técnicos"
        
        # Determinar número de subplots necesarios
        price_indicators = ['sma_20', 'sma_50', 'ema_12', 'ema_26', 'bb_upper', 'bb_middle', 'bb_lower']
        oscillators = ['rsi', 'stoch_k', 'stoch_d', 'cci']
        volume_indicators = ['volume', 'volume_sma']
        macd_indicators = ['macd', 'macd_signal', 'macd_histogram']
        
        subplots_needed = 1  # Precio siempre se muestra
        if any(ind in indicators for ind in oscillators):
            subplots_needed += 1
        if any(ind in indicators for ind in volume_indicators):
            subplots_needed += 1
        if any(ind in indicators for ind in macd_indicators):
            subplots_needed += 1
        
        subplot_titles = ['Precio']
        if any(ind in indicators for ind in oscillators):
            subplot_titles.append('Osciladores')
        if any(ind in indicators for ind in volume_indicators):
            subplot_titles.append('Volumen')
        if any(ind in indicators for ind in macd_indicators):
            subplot_titles.append('MACD')
        
        fig = sp.make_subplots(
            rows=subplots_needed, cols=1,
            subplot_titles=subplot_titles,
            vertical_spacing=0.08,
            shared_xaxes=True
        )
        
        current_row = 1
        
        # 1. Gráfico de precio
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name="Precio",
                showlegend=False
            ),
            row=current_row, col=1
        )
        
        # Agregar indicadores de precio
        for ind in indicators:
            if ind in price_indicators and ind in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[ind],
                        mode='lines',
                        name=ind.upper(),
                        line=dict(width=1)
                    ),
                    row=current_row, col=1
                )
        
        current_row += 1
        
        # 2. Osciladores
        if any(ind in indicators for ind in oscillators):
            for ind in indicators:
                if ind in oscillators and ind in data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data[ind],
                            mode='lines',
                            name=ind.upper(),
                            line=dict(width=2)
                        ),
                        row=current_row, col=1
                    )
            
            # Líneas de referencia para RSI
            if 'rsi' in indicators:
                fig.add_hline(y=70, line_dash="dash", line_color="red", 
                            annotation_text="Sobrecompra", row=current_row, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", 
                            annotation_text="Sobreventa", row=current_row, col=1)
            
            current_row += 1
        
        # 3. Volumen
        if any(ind in indicators for ind in volume_indicators):
            if 'volume' in data.columns:
                fig.add_trace(
                    go.Bar(
                        x=data.index,
                        y=data['volume'],
                        name='Volumen',
                        marker_color='lightblue',
                        opacity=0.7
                    ),
                    row=current_row, col=1
                )
            
            if 'volume_sma' in indicators and 'volume_sma' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['volume_sma'],
                        mode='lines',
                        name='Volumen SMA',
                        line=dict(color='orange', width=2)
                    ),
                    row=current_row, col=1
                )
            
            current_row += 1
        
        # 4. MACD
        if any(ind in indicators for ind in macd_indicators):
            if 'macd' in indicators and 'macd' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue', width=2)
                    ),
                    row=current_row, col=1
                )
            
            if 'macd_signal' in indicators and 'macd_signal' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd_signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color='red', width=2)
                    ),
                    row=current_row, col=1
                )
            
            if 'macd_histogram' in indicators and 'macd_histogram' in data.columns:
                colors = ['green' if x > 0 else 'red' for x in data['macd_histogram']]
                fig.add_trace(
                    go.Bar(
                        x=data.index,
                        y=data['macd_histogram'],
                        name='Histogram',
                        marker_color=colors,
                        opacity=0.7
                    ),
                    row=current_row, col=1
                )
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=300 * subplots_needed,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    @staticmethod
    def save_chart(fig: go.Figure, filename: str, format: str = "html"):
        """
        Guarda el gráfico en archivo
        
        Args:
            fig: Figura de Plotly
            filename: Nombre del archivo
            format: Formato (html, png, jpg, pdf)
        """
        if format.lower() == "html":
            plot(fig, filename=filename, auto_open=False)
        else:
            fig.write_image(filename, format=format)
        
        print(f"Gráfico guardado: {filename}")