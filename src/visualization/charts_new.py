import plotly.graph_objects as go
import plotly.subplots as sp
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Tuple
from plotly.offline import plot

from src.backtester.metrics import BacktestResults, Trade
from src.strategies.base import TradeSignal, SignalType
from src.visualization.advanced_charts import AdvancedChartGenerator


class ChartGenerator:
    """Generador de gráficos para análisis de backtesting mejorado"""
    
    @staticmethod
    def plot_trading_signals_advanced(data: pd.DataFrame, trades: List[Trade], 
                                    indicators: Optional[Dict] = None,
                                    symbol: str = "CRYPTO", 
                                    title: Optional[str] = None) -> go.Figure:
        """
        Gráfico avanzado con señales de long/short usando el nuevo sistema mejorado
        """
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
    
    @staticmethod
    def plot_trade_analysis(results: BacktestResults, data: pd.DataFrame) -> go.Figure:
        """
        Gráfico de análisis de trades y rendimiento mejorado
        """
        # Crear figura con múltiples subplots para análisis completo
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=['💰 Equity Curve', '📊 P&L Distribution', 
                           '⏱️ Trade Duration', '🎯 Win/Loss Analysis'],
            specs=[[{"colspan": 2}, None],
                   [{}, {}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # Configurar colores del tema
        colors = {
            'background': '#0E1117',
            'paper': '#1A1D23', 
            'text': '#FAFAFA',
            'grid': '#2A2E39',
            'profit': '#4CAF50',
            'loss': '#F44336',
            'neutral': '#FF9800'
        }
        
        # 1. Equity Curve (gráfico principal)
        equity_values = []
        cumulative_pnl = 0
        dates = []
        trade_numbers = []
        
        for i, trade in enumerate(results.trades):
            cumulative_pnl += trade.pnl
            equity_values.append(cumulative_pnl)
            dates.append(trade.exit_time if trade.exit_time else trade.entry_time)
            trade_numbers.append(i + 1)
        
        if equity_values:
            fig.add_trace(go.Scatter(
                x=dates,
                y=equity_values,
                mode='lines+markers',
                name='💰 Equity Curve',
                line=dict(color=colors['profit'], width=3),
                marker=dict(size=4, color=colors['profit']),
                hovertemplate='<b>Equity</b><br>Trade: %{text}<br>Fecha: %{x}<br>Valor: $%{y:,.2f}<extra></extra>',
                text=trade_numbers
            ), row=1, col=1)
            
            # Línea de break-even
            fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.5)", 
                         line_width=1, row=1, col=1)
        
        # 2. Distribución de P&L por trade
        if results.trades:
            pnl_values = [trade.pnl for trade in results.trades]
            colors_pnl = [colors['profit'] if pnl > 0 else colors['loss'] for pnl in pnl_values]
            
            fig.add_trace(go.Bar(
                x=list(range(1, len(pnl_values) + 1)),
                y=pnl_values,
                name='📊 P&L por Trade',
                marker_color=colors_pnl,
                opacity=0.8,
                hovertemplate='<b>Trade %{x}</b><br>P&L: $%{y:,.2f}<br>Tipo: %{text}<extra></extra>',
                text=['Ganancia' if pnl > 0 else 'Pérdida' for pnl in pnl_values]
            ), row=2, col=1)
        
        # 3. Distribución de duración de trades
        durations = []
        duration_labels = []
        for trade in results.trades:
            if trade.exit_time and trade.entry_time:
                duration_hours = (trade.exit_time - trade.entry_time).total_seconds() / 3600
                durations.append(duration_hours)
                if duration_hours < 1:
                    duration_labels.append(f"{duration_hours*60:.0f}m")
                elif duration_hours < 24:
                    duration_labels.append(f"{duration_hours:.1f}h")
                else:
                    duration_labels.append(f"{duration_hours/24:.1f}d")
        
        if durations:
            fig.add_trace(go.Histogram(
                x=durations,
                nbinsx=min(20, len(durations)),
                name='⏱️ Duración (horas)',
                marker_color=colors['neutral'],
                opacity=0.7,
                hovertemplate='<b>Duración</b><br>Rango: %{x:.1f}h<br>Cantidad: %{y}<extra></extra>'
            ), row=2, col=2)
        
        # Calcular estadísticas
        total_trades = len(results.trades)
        winning_trades = len([t for t in results.trades if t.pnl > 0])
        losing_trades = len([t for t in results.trades if t.pnl < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = sum(t.pnl for t in results.trades if t.pnl > 0)
        total_loss = sum(t.pnl for t in results.trades if t.pnl < 0)
        profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
        
        # Configurar layout con estadísticas en título
        title_text = (f"📈 Análisis de Performance - {total_trades} Trades | "
                     f"🎯 {win_rate:.1f}% Win Rate | "
                     f"💰 ${sum(t.pnl for t in results.trades):,.2f} Total P&L | "
                     f"📊 PF: {profit_factor:.2f}")
        
        fig.update_layout(
            title=dict(
                text=title_text,
                x=0.5,
                font=dict(size=18, color=colors['text'])
            ),
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['paper'],
            font=dict(color=colors['text'], family="Roboto, sans-serif"),
            height=700,
            margin=dict(l=60, r=60, t=100, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(26,29,35,0.8)",
                bordercolor="rgba(250,250,250,0.2)",
                borderwidth=1
            ),
            hovermode='closest'
        )
        
        # Configurar ejes con grid
        for row in range(1, 3):
            for col in range(1, 3):
                if not (row == 1 and col == 2):  # Skip empty subplot
                    fig.update_xaxes(
                        gridcolor=colors['grid'], 
                        gridwidth=0.5, 
                        showgrid=True,
                        row=row, col=col
                    )
                    fig.update_yaxes(
                        gridcolor=colors['grid'], 
                        gridwidth=0.5, 
                        showgrid=True,
                        row=row, col=col
                    )
        
        # Etiquetas de ejes específicas
        fig.update_xaxes(title_text="Fecha", row=1, col=1)
        fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
        fig.update_xaxes(title_text="Número de Trade", row=2, col=1)
        fig.update_yaxes(title_text="P&L ($)", row=2, col=1)
        fig.update_xaxes(title_text="Duración (horas)", row=2, col=2)
        fig.update_yaxes(title_text="Frecuencia", row=2, col=2)
        
        return fig