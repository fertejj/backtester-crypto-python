import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any, Optional
from src.backtester.metrics import Trade


def create_professional_plotly_chart(data: pd.DataFrame, trades: List[Trade], 
                                    symbol: str = "CRYPTO", indicators: Optional[Dict] = None):
    """Gráfico profesional usando Plotly que simula el estilo TradingView"""
    
    st.info(f"📊 **Gráfico Plotly Profesional:** {len(data)} barras | {len(trades)} trades")
    
    # Crear subplots con volumen
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=[f"📊 {symbol} - Gráfico Profesional de Trading", "📊 Volumen"],
        vertical_spacing=0.05,
        shared_xaxes=True
    )
    
    # Candlesticks principales
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name=symbol,
        increasing_line_color='#00C896',
        decreasing_line_color='#FF4B4B',
        increasing_fillcolor='#00C896',
        decreasing_fillcolor='#FF4B4B'
    ), row=1, col=1)
    
    # Volumen (si está disponible)
    if 'volume' in data.columns:
        colors = ['#00C896' if close >= open else '#FF4B4B' 
                 for close, open in zip(data['close'], data['open'])]
        
        fig.add_trace(go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volumen',
            marker_color=colors,
            opacity=0.6
        ), row=2, col=1)
    
    # Indicadores técnicos
    if indicators:
        colors = {
            'ema_fast': '#FF9800',
            'ema_medium': '#2196F3', 
            'ema_slow': '#E91E63',
            'ema_20': '#FF9800',
            'ema_50': '#2196F3',
            'ema_200': '#E91E63',
            'bb_upper': '#9C27B0',
            'bb_lower': '#9C27B0',
            'bb_middle': '#673AB7'
        }
        
        for name, values in indicators.items():
            if values is not None and len(values) > 0:
                color = colors.get(name, '#666666')
                width = 3 if '200' in name or 'slow' in name else 2
                
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=values,
                    mode='lines',
                    name=name.upper(),
                    line=dict(color=color, width=width),
                    opacity=0.8
                ), row=1, col=1)
    
    # Señales de trading con estilo profesional y MUY VISIBLE
    entry_annotations = []
    exit_annotations = []
    
    for i, trade in enumerate(trades):
        if trade.entry_time and trade.entry_time in data.index:
            # Obtener el precio high/low de la barra para posicionar mejor las señales
            bar_data = data.loc[trade.entry_time]
            
            if trade.side.lower() == 'long':
                # LONG: Señal ABAJO de la barra
                signal_y = bar_data['low'] * 0.998  # Un poco abajo del low
                color = '#00E676'
                arrow_symbol = '▲'
                text_y_offset = -30
                marker_symbol = 'triangle-up'
            else:
                # SHORT: Señal ARRIBA de la barra  
                signal_y = bar_data['high'] * 1.002  # Un poco arriba del high
                color = '#FF5722'
                arrow_symbol = '▼'
                text_y_offset = 30
                marker_symbol = 'triangle-down'
            
            # SEÑAL DE ENTRADA - MUY GRANDE Y VISIBLE
            fig.add_trace(go.Scatter(
                x=[trade.entry_time],
                y=[signal_y],
                mode='markers',
                marker=dict(
                    symbol=marker_symbol,
                    size=25,  # MUY GRANDE
                    color=color,
                    line=dict(color='white', width=3)
                ),
                name=f"Entry {i+1}",
                showlegend=False,
                hovertemplate=f"<b>🎯 {trade.side.upper()} ENTRY</b><br>" +
                             f"� Precio: ${trade.entry_price:.4f}<br>" +
                             f"⏰ Tiempo: {trade.entry_time}<br>" +
                             f"<extra></extra>"
            ), row=1, col=1)
            
            # TEXTO DE ENTRADA - GRANDE Y CLARO
            entry_annotations.append(
                dict(
                    x=trade.entry_time,
                    y=signal_y,
                    xref='x',
                    yref='y',
                    text=f"<b>{arrow_symbol} {trade.side.upper()}</b><br><b>${trade.entry_price:.2f}</b>",
                    showarrow=False,
                    font=dict(
                        family="Arial Black",
                        size=12,
                        color="white"
                    ),
                    bgcolor=color,
                    bordercolor="white",
                    borderwidth=2,
                    borderpad=4,
                    yshift=text_y_offset
                )
            )
            
            # Señal de salida si existe
            if trade.exit_time and trade.exit_price and trade.exit_time in data.index:
                exit_bar_data = data.loc[trade.exit_time]
                exit_color = '#4CAF50' if trade.pnl > 0 else '#F44336'
                pnl_emoji = '💚' if trade.pnl > 0 else '❌'
                
                if trade.side.lower() == 'long':
                    # EXIT LONG: Señal ARRIBA de la barra
                    exit_signal_y = exit_bar_data['high'] * 1.002
                    exit_marker_symbol = 'triangle-down'
                    exit_text_y_offset = 30
                    exit_arrow = '▼'
                else:
                    # EXIT SHORT: Señal ABAJO de la barra
                    exit_signal_y = exit_bar_data['low'] * 0.998
                    exit_marker_symbol = 'triangle-up'
                    exit_text_y_offset = -30
                    exit_arrow = '▲'
                
                # SEÑAL DE SALIDA - MUY GRANDE Y VISIBLE
                fig.add_trace(go.Scatter(
                    x=[trade.exit_time],
                    y=[exit_signal_y],
                    mode='markers',
                    marker=dict(
                        symbol=exit_marker_symbol,
                        size=22,  # GRANDE
                        color=exit_color,
                        line=dict(color='white', width=3)
                    ),
                    name=f"Exit {i+1}",
                    showlegend=False,
                    hovertemplate=f"<b>🏁 EXIT</b><br>" +
                                 f"💰 Precio: ${trade.exit_price:.4f}<br>" +
                                 f"📊 P&L: ${trade.pnl:.2f} ({((trade.exit_price/trade.entry_price - 1) * 100):.1f}%)<br>" +
                                 f"⏰ Tiempo: {trade.exit_time}<br>" +
                                 f"<extra></extra>"
                ), row=1, col=1)
                
                # TEXTO DE SALIDA - GRANDE Y CLARO
                exit_annotations.append(
                    dict(
                        x=trade.exit_time,
                        y=exit_signal_y,
                        xref='x',
                        yref='y',
                        text=f"<b>{exit_arrow} EXIT</b><br><b>${trade.exit_price:.2f}</b><br><b>{pnl_emoji} ${trade.pnl:.1f}</b>",
                        showarrow=False,
                        font=dict(
                            family="Arial Black",
                            size=11,
                            color="white"
                        ),
                        bgcolor=exit_color,
                        bordercolor="white",
                        borderwidth=2,
                        borderpad=4,
                        yshift=exit_text_y_offset
                    )
                )
                
                # LÍNEA CONECTORA MÁS VISIBLE entre entrada y salida
                fig.add_trace(go.Scatter(
                    x=[trade.entry_time, trade.exit_time],
                    y=[trade.entry_price, trade.exit_price],
                    mode='lines',
                    line=dict(
                        color=exit_color,
                        width=3,  # Línea más gruesa
                        dash='dot'
                    ),
                    opacity=0.8,  # Más opaca
                    showlegend=False,
                    hoverinfo='skip'
                ), row=1, col=1)
                
                # ÁREA SOMBREADA para mostrar el trade completo
                fig.add_shape(
                    type="rect",
                    x0=trade.entry_time,
                    x1=trade.exit_time,
                    y0=min(trade.entry_price, trade.exit_price) * 0.9995,
                    y1=max(trade.entry_price, trade.exit_price) * 1.0005,
                    fillcolor=exit_color,
                    opacity=0.1,
                    line=dict(color=exit_color, width=1, dash="dash"),
                    row=1, col=1
                )
    
    # Configuración del layout profesional
    fig.update_layout(
        title=dict(
            text=f"📊 {symbol} - Análisis Profesional de Trading",
            font=dict(size=20, family="Arial Black", color="#333")
        ),
        template="plotly_white",
        height=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        margin=dict(t=80, b=40, l=60, r=60),
        # Agregar todas las anotaciones de señales
        annotations=entry_annotations + exit_annotations
    )
    
    # Configurar ejes
    fig.update_xaxes(
        title_text="Tiempo",
        showgrid=True,
        gridcolor='#f0f0f0',
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text="Precio ($)",
        showgrid=True,
        gridcolor='#f0f0f0',
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text="Volumen",
        showgrid=True,
        gridcolor='#f0f0f0',
        row=2, col=1
    )
    
    # Remover rangeslider para un look más profesional
    fig.update_layout(xaxis_rangeslider_visible=False)
    
    # Mostrar el gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Información detallada de las señales
    if len(trades) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            long_trades = [t for t in trades if t.side.lower() == 'long']
            st.metric("🟢 Trades LONG", len(long_trades))
        with col2:
            short_trades = [t for t in trades if t.side.lower() == 'short']
            st.metric("🔴 Trades SHORT", len(short_trades))
        with col3:
            profitable_trades = [t for t in trades if t.pnl > 0]
            win_rate = len(profitable_trades) / len(trades) * 100 if trades else 0
            st.metric("🎯 Win Rate", f"{win_rate:.1f}%")
    
    st.success("✅ Gráfico profesional con señales MUY VISIBLES - Entradas/Salidas claramente marcadas")
    
    # Leyenda de señales
    st.info("""
    📊 **Leyenda de Señales:**
    - 🟢 ▲ **LONG Entry:** Flecha verde hacia ARRIBA debajo de la barra
    - 🔴 ▼ **SHORT Entry:** Flecha roja hacia ABAJO arriba de la barra  
    - 💚 ▼ **EXIT Ganancia:** Flecha verde de salida con P&L positivo
    - ❌ ▲ **EXIT Pérdida:** Flecha roja de salida con P&L negativo
    - 🔗 **Líneas punteadas:** Conectan entrada con salida del mismo trade
    - 🟦 **Áreas sombreadas:** Duración completa de cada trade
    """)


def create_simple_candlestick_chart(data: pd.DataFrame, trades: List[Trade], 
                                   symbol: str = "CRYPTO"):
    """Gráfico de candlesticks simple y rápido"""
    
    fig = go.Figure(data=go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name=symbol,
        increasing_line_color='#00C896',
        decreasing_line_color='#FF4B4B'
    ))
    
    # Añadir señales básicas
    for trade in trades:
        if trade.entry_time:
            color = '#00E676' if trade.side.lower() == 'long' else '#FF5722'
            fig.add_scatter(
                x=[trade.entry_time],
                y=[trade.entry_price],
                mode='markers',
                marker=dict(
                    symbol='triangle-up' if trade.side.lower() == 'long' else 'triangle-down',
                    size=12,
                    color=color
                ),
                name=trade.side.upper(),
                showlegend=False
            )
    
    fig.update_layout(
        title=f"📊 {symbol} - Gráfico Básico",
        xaxis_title="Tiempo",
        yaxis_title="Precio ($)",
        template="plotly_white",
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("📊 Gráfico básico de candlesticks")