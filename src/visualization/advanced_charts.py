import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Tuple, Any
from plotly.offline import plot
from datetime import datetime, timedelta

from src.backtester.metrics import BacktestResults, Trade
from src.strategies.base import TradeSignal, SignalType


class ChartConfig:
    """Configuración avanzada para gráficos de trading"""
    
    def __init__(self):
        # Colores del tema claro profesional
        self.colors = {
            'background': '#FFFFFF',
            'paper': '#FAFAFA', 
            'text': '#2E2E2E',
            'grid': '#E0E0E0',
            'candle_up': '#00C896',
            'candle_down': '#FF4B4B',
            'volume_up': 'rgba(0, 200, 150, 0.6)',
            'volume_down': 'rgba(255, 75, 75, 0.6)',
            'long_entry': '#00C853',
            'long_exit': '#2E7D32',
            'short_entry': '#D32F2F',
            'short_exit': '#F57C00',
            'profit_line': '#2E7D32',
            'loss_line': '#D32F2F',
            'ema_fast': '#FF9800',
            'ema_slow': '#2196F3',
            'ema_trend': '#E91E63',
            'rsi': '#9C27B0',
            'macd': '#FF5722',
            'macd_signal': '#3F51B5',
            'macd_hist': '#4CAF50',
            'bb': '#673AB7',
            'support': '#FFC107',
            'resistance': '#F44336'
        }
        
        # Configuración de layout
        self.layout_config = {
            'height': 900,
            'margin': dict(l=80, r=80, t=100, b=80),
            'font': dict(family="Roboto, Arial, sans-serif", size=12, color=self.colors['text']),
            'hovermode': 'x unified',
            'dragmode': 'zoom',
            'showlegend': True,
            'legend': dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="rgba(46,46,46,0.2)",
                borderwidth=1,
                font=dict(size=11)
            ),
            'xaxis': dict(
                gridcolor=self.colors['grid'],
                gridwidth=1,
                showgrid=True,
                zeroline=False,
                rangeslider=dict(visible=False)
            ),
            'yaxis': dict(
                gridcolor=self.colors['grid'],
                gridwidth=1,
                showgrid=True,
                zeroline=False
            )
        }
        
        # Configuración de marcadores
        self.markers = {
            'long_entry': dict(symbol='triangle-up', size=20, line=dict(width=3, color='#2E7D32')),
            'long_exit': dict(symbol='triangle-down', size=16, line=dict(width=2, color='#1B5E20')),
            'short_entry': dict(symbol='triangle-down', size=20, line=dict(width=3, color='#C62828')),
            'short_exit': dict(symbol='triangle-up', size=16, line=dict(width=2, color='#E65100'))
        }


class AdvancedChartGenerator:
    """Generador avanzado de gráficos con máximo control y claridad"""
    
    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
    
    def create_professional_trading_chart(self, 
                                        data: pd.DataFrame, 
                                        trades: List[Trade],
                                        indicators: Optional[Dict] = None,
                                        symbol: str = "CRYPTO",
                                        timeframe: str = "1h",
                                        show_volume: bool = True,
                                        show_trade_lines: bool = True,
                                        show_levels: bool = True,
                                        chart_style: str = "professional") -> go.Figure:
        """
        Crea un gráfico de trading profesional con control total
        
        Args:
            data: DataFrame con datos OHLC
            trades: Lista de trades ejecutados  
            indicators: Diccionario con indicadores técnicos
            symbol: Símbolo del activo
            timeframe: Timeframe de los datos
            show_volume: Mostrar volumen
            show_trade_lines: Mostrar líneas de trades
            show_levels: Mostrar niveles de soporte/resistencia
            chart_style: Estilo del gráfico ('professional', 'minimal', 'detailed')
        """
        
        # 1. Preparar estructura de subplots
        subplot_config = self._calculate_subplot_layout(indicators, show_volume)
        
        # 2. Crear figura con subplots
        fig = self._create_figure_structure(subplot_config, symbol, timeframe)
        
        # 3. Agregar candlesticks principales
        self._add_main_candlesticks(fig, data)
        
        # 4. Agregar indicadores técnicos
        if indicators:
            self._add_all_indicators(fig, data, indicators, subplot_config)
        
        # 5. Agregar volumen si se solicita
        if show_volume and 'volume' in data.columns:
            self._add_volume_analysis(fig, data, subplot_config.get('volume_row'))
        
        # 6. Agregar señales de trading detalladas
        self._add_detailed_trading_signals(fig, trades, show_trade_lines)
        
        # 7. Agregar niveles técnicos
        if show_levels:
            self._add_technical_levels(fig, data)
        
        # 8. Configurar layout final
        self._apply_final_styling(fig, trades, data, chart_style, subplot_config)
        
        return fig
    
    def _calculate_subplot_layout(self, indicators: Optional[Dict], show_volume: bool) -> Dict[str, Any]:
        """Calcula la disposición óptima de subplots"""
        layout = {
            'total_rows': 1,
            'main_row': 1,
            'titles': ['📈 Precio y Señales de Trading'],
            'heights': [1.0],
            'volume_row': None,
            'rsi_row': None, 
            'macd_row': None,
            'stoch_row': None
        }
        
        current_row = 1
        
        # Volumen
        if show_volume:
            current_row += 1
            layout['volume_row'] = current_row
            layout['total_rows'] = current_row
            layout['titles'].append('📊 Volumen')
            layout['heights'] = [0.65, 0.2]
        
        # RSI
        if indicators and 'rsi' in indicators:
            current_row += 1
            layout['rsi_row'] = current_row
            layout['total_rows'] = current_row
            layout['titles'].append('📉 RSI (14)')
            self._adjust_heights(layout, 'rsi')
        
        # MACD  
        if indicators and any(k in ['macd', 'macd_signal', 'macd_histogram'] for k in indicators.keys()):
            current_row += 1
            layout['macd_row'] = current_row
            layout['total_rows'] = current_row
            layout['titles'].append('📊 MACD')
            self._adjust_heights(layout, 'macd')
        
        return layout
    
    def _adjust_heights(self, layout: Dict, indicator_type: str):
        """Ajusta las alturas de los subplots según indicadores"""
        total_indicators = sum([1 for k in ['volume_row', 'rsi_row', 'macd_row'] 
                               if layout.get(k) is not None])
        
        if total_indicators == 1:
            layout['heights'] = [0.7, 0.3]
        elif total_indicators == 2:
            layout['heights'] = [0.6, 0.2, 0.2]
        elif total_indicators == 3:
            layout['heights'] = [0.5, 0.15, 0.2, 0.15]
        else:
            layout['heights'] = [0.45] + [0.55 / total_indicators] * total_indicators
    
    def _create_figure_structure(self, config: Dict, symbol: str, timeframe: str) -> go.Figure:
        """Crea la estructura base de la figura"""
        title = f"⚡ {symbol} ({timeframe.upper()}) - Análisis Profesional de Trading"
        
        fig = sp.make_subplots(
            rows=config['total_rows'],
            cols=1,
            subplot_titles=config['titles'],
            vertical_spacing=0.03,
            row_heights=config['heights'],
            shared_xaxes=True
        )
        
        # Configurar tema base
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=22, weight='bold', color=self.config.colors['text'])
            ),
            plot_bgcolor=self.config.colors['background'],
            paper_bgcolor=self.config.colors['paper'],
            **self.config.layout_config
        )
        
        return fig
    
    def _add_main_candlesticks(self, fig: go.Figure, data: pd.DataFrame):
        """Agrega candlesticks con estilo profesional"""
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="💰 Precio",
            increasing_line_color=self.config.colors['candle_up'],
            decreasing_line_color=self.config.colors['candle_down'],
            increasing_fillcolor=self.config.colors['candle_up'],
            decreasing_fillcolor=self.config.colors['candle_down'],
            line=dict(width=1.2),
            showlegend=True,
            text=[f'📅 {idx}<br>� Open: ${row["open"]:,.4f}<br>⬆️ High: ${row["high"]:,.4f}<br>⬇️ Low: ${row["low"]:,.4f}<br>🔒 Close: ${row["close"]:,.4f}'
                  for idx, row in data.iterrows()],
            hovertext=[f'� {idx}<br>�🔓 Open: ${row["open"]:,.4f}<br>⬆️ High: ${row["high"]:,.4f}<br>⬇️ Low: ${row["low"]:,.4f}<br>🔒 Close: ${row["close"]:,.4f}'
                      for idx, row in data.iterrows()],
            hoverinfo='text'
        ), row=1, col=1)
    
    def _add_all_indicators(self, fig: go.Figure, data: pd.DataFrame, 
                           indicators: Dict, config: Dict):
        """Agrega todos los indicadores técnicos con estilo mejorado"""
        
        # EMAs en gráfico principal
        ema_colors = {
            'ema_20': self.config.colors['ema_fast'],
            'ema_55': self.config.colors['ema_slow'], 
            'ema_200': self.config.colors['ema_trend'],
            'ema_fast': self.config.colors['ema_fast'],
            'ema_slow': self.config.colors['ema_slow']
        }
        
        for key, values in indicators.items():
            if 'ema' in key.lower() and values is not None:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=values,
                    mode='lines',
                    name=f"📊 {key.upper().replace('_', ' ')}",
                    line=dict(
                        color=ema_colors.get(key, '#999999'), 
                        width=2.5 if '200' in key else 2
                    ),
                    opacity=0.9,
                    hovertemplate=f'<b>{key.upper()}</b><br>Valor: %{{y:,.4f}}<extra></extra>'
                ), row=1, col=1)
        
        # Bollinger Bands
        if 'bb_upper' in indicators and 'bb_lower' in indicators:
            # Banda superior
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['bb_upper'],
                mode='lines',
                name='📈 BB Superior',
                line=dict(color=self.config.colors['bb'], width=1, dash='dash'),
                opacity=0.7,
                showlegend=True
            ), row=1, col=1)
            
            # Banda inferior con relleno
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['bb_lower'],
                mode='lines',
                name='📉 BB Inferior',
                line=dict(color=self.config.colors['bb'], width=1, dash='dash'),
                fill='tonexty',
                fillcolor=f"rgba({int(self.config.colors['bb'][1:3], 16)}, "
                         f"{int(self.config.colors['bb'][3:5], 16)}, "
                         f"{int(self.config.colors['bb'][5:7], 16)}, 0.1)",
                opacity=0.7
            ), row=1, col=1)
        
        # RSI en subplot dedicado
        if config.get('rsi_row') and 'rsi' in indicators:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['rsi'],
                mode='lines',
                name='📊 RSI',
                line=dict(color=self.config.colors['rsi'], width=2.5),
                hovertemplate='<b>RSI</b><br>Valor: %{y:.2f}<extra></extra>'
            ), row=config['rsi_row'], col=1)
            
            # Líneas de referencia RSI
            fig.add_hline(
                y=70, line_dash="dash", line_color="rgba(255,75,75,0.8)",
                annotation_text="⚠️ Sobrecompra (70)", annotation_position="right",
                row=config['rsi_row'], col=1
            )
            fig.add_hline(
                y=30, line_dash="dash", line_color="rgba(0,200,150,0.8)", 
                annotation_text="💡 Sobreventa (30)", annotation_position="right",
                row=config['rsi_row'], col=1
            )
            fig.add_hline(
                y=50, line_dash="dot", line_color="rgba(46,46,46,0.4)",
                row=config['rsi_row'], col=1
            )
            
            fig.update_yaxes(range=[0, 100], title_text="RSI", row=config['rsi_row'], col=1)
        
        # MACD en subplot dedicado
        if config.get('macd_row'):
            self._add_macd_subplot(fig, data, indicators, config['macd_row'])
    
    def _add_macd_subplot(self, fig: go.Figure, data: pd.DataFrame, 
                         indicators: Dict, macd_row: int):
        """Agrega subplot de MACD con histograma"""
        if 'macd' in indicators:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['macd'],
                mode='lines',
                name='📊 MACD',
                line=dict(color=self.config.colors['macd'], width=2)
            ), row=macd_row, col=1)
        
        if 'macd_signal' in indicators:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['macd_signal'],
                mode='lines',
                name='📈 Señal',
                line=dict(color=self.config.colors['macd_signal'], width=2)
            ), row=macd_row, col=1)
        
        if 'macd_histogram' in indicators:
            colors = ['rgba(76,175,80,0.8)' if val >= 0 else 'rgba(244,67,54,0.8)' 
                     for val in indicators['macd_histogram']]
            
            fig.add_trace(go.Bar(
                x=data.index,
                y=indicators['macd_histogram'],
                name='📊 Histograma',
                marker_color=colors,
                opacity=0.7
            ), row=macd_row, col=1)
        
        fig.add_hline(y=0, line_color="rgba(46,46,46,0.5)", line_width=1, 
                     row=macd_row, col=1)
        fig.update_yaxes(title_text="MACD", row=macd_row, col=1)
    
    def _add_volume_analysis(self, fig: go.Figure, data: pd.DataFrame, volume_row: Optional[int]):
        """Agrega análisis de volumen avanzado"""
        if volume_row is None:
            return
        
        # Colores según la dirección del precio
        colors = []
        for i in range(len(data)):
            if data.iloc[i]['close'] >= data.iloc[i]['open']:
                colors.append(self.config.colors['volume_up'])
            else:
                colors.append(self.config.colors['volume_down'])
        
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['volume'],
            name='📊 Volumen',
            marker_color=colors,
            opacity=0.8,
            hovertemplate='<b>📊 Volumen</b><br>' +
                         'Fecha: %{x}<br>' +
                         'Volumen: %{y:,.0f}<br>' +
                         '<extra></extra>'
        ), row=volume_row, col=1)
        
        # Agregar línea de promedio móvil del volumen
        if len(data) > 20:
            vol_ma = data['volume'].rolling(20).mean()
            fig.add_trace(go.Scatter(
                x=data.index,
                y=vol_ma,
                mode='lines',
                name='📈 Vol MA(20)',
                line=dict(color='rgba(46,46,46,0.7)', width=1.5, dash='dash'),
                opacity=0.8
            ), row=volume_row, col=1)
        
        fig.update_yaxes(title_text="Volumen", row=volume_row, col=1)
    
    def _add_detailed_trading_signals(self, fig: go.Figure, trades: List[Trade], 
                                    show_trade_lines: bool):
        """Agrega señales de trading con máximo detalle"""
        
        # Separar trades por tipo y resultado
        long_entries, long_exits = [], []
        short_entries, short_exits = [], []
        profitable_trades, losing_trades = [], []
        
        for trade in trades:
            entry_point = (trade.entry_time, trade.entry_price)
            exit_point = (trade.exit_time, trade.exit_price) if trade.exit_time else None
            
            if trade.side.lower() == 'long':
                long_entries.append(entry_point)
                if exit_point:
                    long_exits.append(exit_point)
            else:
                short_entries.append(entry_point)  
                if exit_point:
                    short_exits.append(exit_point)
            
            # Clasificar por rentabilidad
            if trade.pnl > 0:
                profitable_trades.append(trade)
            else:
                losing_trades.append(trade)
        
        # Señales LONG
        if long_entries:
            fig.add_trace(go.Scatter(
                x=[entry[0] for entry in long_entries],
                y=[entry[1] for entry in long_entries],
                mode='markers',
                marker=dict(
                    color=self.config.colors['long_entry'],
                    **self.config.markers['long_entry']
                ),
                name='🚀 Long Entry',
                hovertemplate='<b>🟢 LONG ENTRY</b><br>' +
                             '📅 %{x}<br>' +
                             '💰 $%{y:,.4f}<br>' +
                             '<extra></extra>'
            ), row=1, col=1)
        
        if long_exits:
            fig.add_trace(go.Scatter(
                x=[exit[0] for exit in long_exits],
                y=[exit[1] for exit in long_exits],
                mode='markers',
                marker=dict(
                    color=self.config.colors['long_exit'],
                    **self.config.markers['long_exit']
                ),
                name='🔻 Long Exit',
                hovertemplate='<b>🔴 LONG EXIT</b><br>' +
                             '📅 %{x}<br>' +
                             '💰 $%{y:,.4f}<br>' +
                             '<extra></extra>'
            ), row=1, col=1)
        
        # Señales SHORT
        if short_entries:
            fig.add_trace(go.Scatter(
                x=[entry[0] for entry in short_entries],
                y=[entry[1] for entry in short_entries],
                mode='markers',
                marker=dict(
                    color=self.config.colors['short_entry'],
                    **self.config.markers['short_entry']
                ),
                name='🔻 Short Entry',
                hovertemplate='<b>🔴 SHORT ENTRY</b><br>' +
                             '📅 %{x}<br>' +
                             '💰 $%{y:,.4f}<br>' +
                             '<extra></extra>'
            ), row=1, col=1)
        
        if short_exits:
            fig.add_trace(go.Scatter(
                x=[exit[0] for exit in short_exits],
                y=[exit[1] for exit in short_exits],
                mode='markers',
                marker=dict(
                    color=self.config.colors['short_exit'],
                    **self.config.markers['short_exit']
                ),
                name='🚀 Short Exit',
                hovertemplate='<b>🟢 SHORT EXIT</b><br>' +
                             '📅 %{x}<br>' +
                             '💰 $%{y:,.4f}<br>' +
                             '<extra></extra>'
            ), row=1, col=1)
        
        # Líneas de conexión de trades
        if show_trade_lines:
            for trade in trades:
                if trade.exit_time and trade.exit_price:
                    # Estilo según rentabilidad
                    line_color = self.config.colors['profit_line'] if trade.pnl > 0 else self.config.colors['loss_line']
                    line_width = 3 if abs(trade.pnl) > 50 else 2
                    line_dash = 'solid' if trade.pnl > 0 else 'dot'
                    
                    # Calcular retorno porcentual
                    return_pct = (trade.pnl / trade.entry_price) * 100 if trade.entry_price > 0 else 0
                    
                    fig.add_trace(go.Scatter(
                        x=[trade.entry_time, trade.exit_time],
                        y=[trade.entry_price, trade.exit_price],
                        mode='lines',
                        line=dict(color=line_color, width=line_width, dash=line_dash),
                        opacity=0.7,
                        showlegend=False,
                        hovertemplate=f'<b>{trade.side.upper()} TRADE</b><br>' +
                                     f'💰 P&L: ${trade.pnl:,.2f}<br>' +
                                     f'📊 Return: {return_pct:.2f}%<br>' +
                                     f'⏱️ Duración: {trade.exit_time - trade.entry_time}<br>' +
                                     '<extra></extra>'
                    ), row=1, col=1)
    
    def _add_technical_levels(self, fig: go.Figure, data: pd.DataFrame):
        """Agrega niveles de soporte y resistencia"""
        if len(data) < 50:
            return
        
        # Calcular niveles de soporte y resistencia básicos
        recent_data = data.tail(50)
        resistance = recent_data['high'].max()
        support = recent_data['low'].min()
        
        # Agregar líneas horizontales
        fig.add_hline(
            y=resistance,
            line_dash="dashdot",
            line_color=self.config.colors['resistance'],
            line_width=2,
            annotation_text="⚡ Resistencia",
            annotation_position="right",
            row=1, col=1
        )
        
        fig.add_hline(
            y=support,
            line_dash="dashdot", 
            line_color=self.config.colors['support'],
            line_width=2,
            annotation_text="🛡️ Soporte",
            annotation_position="right",
            row=1, col=1
        )
    
    def _apply_final_styling(self, fig: go.Figure, trades: List[Trade], 
                            data: pd.DataFrame, chart_style: str, subplot_config: Dict):
        """Aplica el estilo final al gráfico"""
        
        # Calcular estadísticas para el título
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        total_pnl = sum(t.pnl for t in trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Actualizar título con métricas
        title_stats = (f" | 📊 {total_trades} trades | "
                      f"🎯 {win_rate:.1f}% win rate | "
                      f"💰 ${total_pnl:,.2f} P&L")
        
        current_title = fig.layout.title.text
        fig.update_layout(title_text=current_title + title_stats)
        
        # Configurar grid y ejes para todos los subplots
        total_rows = subplot_config.get('total_rows', 1)
        
        for i in range(1, total_rows + 1):
            fig.update_xaxes(
                gridcolor=self.config.colors['grid'],
                gridwidth=0.5,
                showgrid=True,
                row=i, col=1
            )
            fig.update_yaxes(
                gridcolor=self.config.colors['grid'],
                gridwidth=0.5,
                showgrid=True,
                row=i, col=1
            )
        
        # Configurar zoom y interactividad
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            dragmode='zoom'
        )
        
        # Agregar botones de control
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(
                            args=[{"visible": [True] * len(fig.data)}],
                            label="📊 Mostrar Todo",
                            method="restyle"
                        ),
                        dict(
                            args=[{"visible": [trace.name and "Entry" in trace.name 
                                              for trace in fig.data]}],
                            label="🎯 Solo Entradas",
                            method="restyle"
                        )
                    ]),
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.01,
                    xanchor="left",
                    y=0.98,
                    yanchor="top"
                )
            ]
        )


# Función de compatibilidad con la API existente
def plot_trading_signals_advanced(data: pd.DataFrame, trades: List[Trade], 
                                indicators: Optional[Dict] = None,
                                symbol: str = "CRYPTO", 
                                title: Optional[str] = None) -> go.Figure:
    """Función de compatibilidad que usa el nuevo generador avanzado"""
    generator = AdvancedChartGenerator()
    return generator.create_professional_trading_chart(
        data=data,
        trades=trades,
        indicators=indicators,
        symbol=symbol,
        show_volume=True,
        show_trade_lines=True,
        show_levels=True,
        chart_style="professional"
    )


def plot_trade_analysis(results: BacktestResults, data: pd.DataFrame) -> go.Figure:
    """Gráfico de análisis de rendimiento mejorado"""
    generator = AdvancedChartGenerator()
    
    # Crear gráfico simple de rendimiento
    fig = go.Figure()
    
    # Equity curve
    fig.add_trace(go.Scatter(
        x=list(range(len(results.trades))),
        y=[sum(t.pnl for t in results.trades[:i+1]) for i in range(len(results.trades))],
        mode='lines+markers',
        name='💰 Equity Curve',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=6, color='#4CAF50')
    ))
    
    fig.update_layout(
        title="📈 Análisis de Rendimiento",
        xaxis_title="Número de Trade",
        yaxis_title="P&L Acumulado ($)",
        plot_bgcolor='#0E1117',
        paper_bgcolor='#1A1D23',
        font=dict(color='#FAFAFA'),
        height=400
    )
    
    return fig