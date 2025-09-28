import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.api.bingx_client import BingXClient
from src.strategies.rsi_strategy import RSIStrategy, MACDStrategy, BollingerBandsStrategy
from src.strategies.ema_strategy import EMAStrategy, EMAGoldenCrossStrategy
from src.backtester.engine import BacktesterEngine
from src.risk.manager import RiskParameters
from src.utils.helpers import format_currency, format_percentage
from src.visualization.charts import ChartGenerator
from src.visualization.tradingview_enhanced import create_enhanced_tradingview_chart, create_fallback_chart
from src.visualization.plotly_professional import create_professional_plotly_chart

def get_icon(name: str) -> str:
    """Función simple para iconos Unicode limpios"""
    icons = {
        "bolt": "⚡",
        "settings": "⚙",
        "database": "💾",
        "chart": "📊",
        "trending": "📈", 
        "strategy": "🧠",
        "shield": "🛡",
        "play": "▶",
        "tool": "🔧",
        "info": "ℹ",
        "check": "✓",
        "warning": "⚠",
        "calendar": "📅",
        "globe": "🌐",
        "dollar": "💰",
        "target": "🎯",
        "time": "⏱",
        "signal": "📡",
        "config": "⚙",
        "advanced": "🔧",
        "search": "🔍",
        "debug": "🐛",
        "green": "🟢",
        "red": "🔴",
        "book": "📚",
        "success": "✅",
        "triangle": "△",
        "dice": "🎲",
        "link": "🔗",
        "eye": "👁",
        "arrow_up": "↑",
        "arrow_down": "↓",
        "circle": "●",
        "star": "⭐",
        "fire": "🔥",
        "rocket": "🚀",
        "gem": "💎",
        "crown": "👑"
    }
    return icons.get(name, "•")


# Configuración de la página
st.set_page_config(
    page_title="Crypto Trading Backtester",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .profit {
        color: #00d4aa;
    }
    .loss {
        color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title(f"{get_icon('bolt')} Crypto Trading Backtester")
    st.markdown("### Analiza y optimiza tus estrategias de trading de criptomonedas")

    # Sidebar - Configuración
    with st.sidebar:
        st.header(f"{get_icon('settings')} Configuración")
        
        # Configuración de datos
        st.subheader(f"{get_icon('database')} Fuente de Datos")
        use_real_data = st.checkbox(
            f"{get_icon('globe')} Usar Datos Reales de BingX", 
            value=False,
            help="Requiere configuración de API keys en archivo .env"
        )
        
        if use_real_data:
            st.info(f"{get_icon('signal')} Usando API real de BingX")
            # Verificar si las credenciales están configuradas
            try:
                from config.settings import settings
                if settings.bingx_api_key == "tu_api_key_aqui":
                    st.warning(f"{get_icon('triangle')} Credenciales API no configuradas")
                    st.markdown(f"{get_icon('book')} **[Ver guía de configuración](API_REAL_SETUP.md)**")
                else:
                    st.success(f"{get_icon('success')} Credenciales API configuradas")
            except:
                st.warning(f"{get_icon('warning')} Configuración API no encontrada")
        else:
            st.info("🎲 Usando datos sintéticos para demo")
        
        # Configuración del activo
        st.subheader(f"{get_icon('trending')} Activo y Período")
        symbol = st.selectbox(
            "Símbolo:", 
            ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "BNBUSDT", "SOLUSDT", "MATICUSDT"],
            index=0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Fecha Inicio:",
                value=date(2024, 1, 1),
                max_value=date.today()
            )
        with col2:
            end_date = st.date_input(
                "Fecha Fin:",
                value=date(2024, 6, 1),
                max_value=date.today()
            )
        
        interval = st.selectbox(
            "Intervalo:",
            ["5m", "15m", "30m", "1h", "4h", "1d", "1w"],
            index=3  # Default a 1h
        )
        
        initial_capital = st.number_input(
            "Capital Inicial ($):",
            min_value=1000,
            max_value=1000000,
            value=10000,
            step=1000
        )
        
        # Configuración de Estrategia
        st.subheader(f"{get_icon('strategy')} Estrategia")
        strategy_type = st.selectbox(
            "Tipo de Estrategia:",
            ["RSI", "MACD", "Bollinger Bands", "EMA Triple", "EMA Golden Cross"]
        )
        
        # Panel dinámico de parámetros según estrategia
        st.markdown("---")
        st.markdown(f"**{get_icon('tool')} Parámetros de la Estrategia:**")
        
        # Parámetros específicos por estrategia
        if strategy_type == "RSI":
            with st.container():
                st.markdown("*Relative Strength Index - Oscilador de momentum*")
                col1, col2 = st.columns(2)
                with col1:
                    rsi_period = st.slider("Período RSI:", 5, 30, 14)
                    buy_threshold = st.slider("Umbral Compra:", 10, 40, 30)
                with col2:
                    sell_threshold = st.slider("Umbral Venta:", 60, 90, 70)
                    st.info(f"{get_icon('info')} Señal Compra: RSI < {buy_threshold} (Sobreventa)")
                    st.info(f"{get_icon('info')} Señal Venta: RSI > {sell_threshold} (Sobrecompra)")
            
        elif strategy_type == "MACD":
            with st.container():
                st.markdown("*Moving Average Convergence Divergence*")
                col1, col2, col3 = st.columns(3)
                with col1:
                    fast_period = st.slider("EMA Rápida:", 5, 20, 12)
                with col2:
                    slow_period = st.slider("EMA Lenta:", 20, 40, 26)
                with col3:
                    signal_period = st.slider("Señal:", 5, 15, 9)
                st.info(f"{get_icon('info')} Señales: Cruces de línea MACD con línea de señal")
            
        elif strategy_type == "Bollinger Bands":
            with st.container():
                st.markdown("*Bandas de Bollinger - Volatilidad*")
                col1, col2 = st.columns(2)
                with col1:
                    bb_period = st.slider("Período BB:", 10, 30, 20)
                with col2:
                    bb_std = st.slider("Desviación Estándar:", 1.5, 3.0, 2.0, 0.1)
                st.info(f"{get_icon('info')} Compra: Precio toca banda inferior | Venta: Precio toca banda superior")
            
        elif strategy_type == "EMA Triple":
            with st.container():
                st.markdown("*Triple EMA con filtros direccionales*")
                
                # Configuración de EMAs
                st.markdown("**◇ Configuración de EMAs:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    fast_ema = st.number_input("EMA Rápida:", 5, 50, 20, 1)
                with col2:
                    medium_ema = st.number_input("EMA Media:", 20, 100, 55, 1)
                with col3:
                    slow_ema = st.number_input("EMA Lenta:", 100, 300, 200, 5)
                
                # Configuración de dirección
                st.markdown("**🎯 Dirección de Trading:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    allow_longs = st.checkbox("🟢 Permitir Longs", value=True)
                with col2:
                    allow_shorts = st.checkbox("🔴 Permitir Shorts", value=False)
                with col3:
                    trend_filter = st.checkbox("🔍 Usar Filtro de Tendencia", value=True, 
                                             help="Usar EMA lenta como filtro direccional")
                
                # Configuración avanzada
                with st.expander(f"{get_icon('advanced')} Configuración Avanzada"):
                    min_trend_strength = st.slider(
                        "Fuerza Mínima de Tendencia:", 
                        0.0001, 0.01, 0.001, 0.0001,
                        format="%.4f",
                        help="Pendiente mínima de EMA rápida para confirmar señal"
                    )
                    
                    st.markdown("**📋 Lógica de la Estrategia:**")
                    st.markdown("""
                    - **Long**: EMA20 > EMA55 > EMA200 + Precio cruza EMA20 hacia arriba
                    - **Short**: EMA20 < EMA55 < EMA200 + Precio cruza EMA20 hacia abajo  
                    - **Filtro**: EMA200 determina tendencia principal
                    - **Confirmación**: Pendiente de EMA20 debe superar umbral mínimo
                    """)
        
        else:  # EMA Golden Cross
            with st.container():
                st.markdown("*EMA Golden Cross - Cruce de medias móviles*")
                col1, col2 = st.columns(2)
                with col1:
                    fast_ema_gc = st.number_input("EMA Rápida:", 20, 100, 50, 5)
                with col2:
                    slow_ema_gc = st.number_input("EMA Lenta:", 100, 300, 200, 10)
                st.info(f"{get_icon('info')} Golden Cross: EMA rápida > EMA lenta | Death Cross: EMA rápida < EMA lenta")
        
        # Gestión de Riesgo
        st.subheader(f"{get_icon('shield')} Gestión de Riesgo Global")
        max_position_size = st.slider("Tamaño Máx. Posición (%):", 5, 50, 20) / 100
        stop_loss_pct = st.slider("Stop Loss (%):", 0, 20, 5) / 100
        take_profit_pct = st.slider("Take Profit (%):", 0, 30, 10) / 100
        risk_per_trade = st.slider("Riesgo por Trade (%):", 1, 10, 2) / 100
        
        # Botón de ejecución
        if st.button(f"{get_icon('play')} Ejecutar Backtest", type="primary", use_container_width=False):
            run_backtest(
                symbol, start_date, end_date, interval, initial_capital,
                strategy_type, locals(), max_position_size, stop_loss_pct,
                take_profit_pct, risk_per_trade, use_real_data
            )

    # Área principal
    if 'results' not in st.session_state:
        st.info(f"{get_icon('arrow_up')} Configura los parámetros en el panel lateral y haz clic en 'Ejecutar Backtest' para comenzar.")
        
        # Mostrar información del proyecto
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **{get_icon('tool')} Características:**
            - Múltiples estrategias de trading
            - Indicadores técnicos avanzados  
            - Gestión de riesgo integrada
            - Métricas de rendimiento detalladas
            """)
        
        with col2:
            st.markdown(f"""
            **{get_icon('strategy')} Estrategias Disponibles:**
            - RSI (Relative Strength Index)
            - MACD (Moving Average Convergence Divergence)
            - Bollinger Bands
            - EMA Triple (20/55/200 con filtros)
            - EMA Golden Cross (50/200)
            """)
        
        with col3:
            st.markdown(f"""
            **{get_icon('chart')} Métricas Calculadas:**
            - Retorno total y anualizado
            - Sharpe Ratio
            - Maximum Drawdown
            - Win Rate y Profit Factor
            """)
    else:
        show_results()


def run_backtest(symbol, start_date, end_date, interval, initial_capital,
                strategy_type, params, max_position_size, stop_loss_pct,
                take_profit_pct, risk_per_trade, use_real_data=False):
    
    with st.spinner('🔄 Ejecutando backtest... Esto puede tomar unos segundos.'):
        try:
            # Crear cliente API según configuración
            if use_real_data:
                try:
                    api_client = BingXClient(use_synthetic=False)
                    st.info("📡 Usando datos reales de BingX API")
                except Exception as e:
                    st.warning(f"⚠️ Error configurando API real: {e}")
                    st.info("🔄 Cambiando a datos sintéticos...")
                    api_client = BingXClient(use_synthetic=True)
            else:
                api_client = BingXClient(use_synthetic=True)
                st.info("🎲 Usando datos sintéticos para demo")
            
            # Crear motor de backtesting
            engine = BacktesterEngine(api_client=api_client, commission=0.001)
            
            # Crear estrategia basada en la selección
            if strategy_type == "RSI":
                strategy = RSIStrategy(
                    symbol=symbol,
                    rsi_period=params['rsi_period'],
                    buy_threshold=params['buy_threshold'],
                    sell_threshold=params['sell_threshold']
                )
            elif strategy_type == "MACD":
                strategy = MACDStrategy(
                    symbol=symbol,
                    fast_period=params['fast_period'],
                    slow_period=params['slow_period'],
                    signal_period=params['signal_period']
                )
            elif strategy_type == "Bollinger Bands":
                strategy = BollingerBandsStrategy(
                    symbol=symbol,
                    bb_period=params['bb_period'],
                    bb_std=params['bb_std']
                )
            elif strategy_type == "EMA Triple":
                strategy = EMAStrategy(
                    symbol=symbol,
                    fast_ema=params['fast_ema'],
                    medium_ema=params['medium_ema'],
                    slow_ema=params['slow_ema'],
                    min_trend_strength=params['min_trend_strength'],
                    allow_longs=params['allow_longs'],
                    allow_shorts=params['allow_shorts'],
                    trend_filter=params['trend_filter']
                )
            else:  # EMA Golden Cross
                strategy = EMAGoldenCrossStrategy(
                    symbol=symbol,
                    fast_ema=params['fast_ema_gc'],
                    slow_ema=params['slow_ema_gc']
                )
            
            # Parámetros de riesgo
            risk_params = RiskParameters(
                max_position_size=max_position_size,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                risk_per_trade=risk_per_trade
            )
            
            # Ejecutar backtest
            results = engine.run_backtest(
                strategy=strategy,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                initial_capital=initial_capital,
                interval=interval,
                risk_params=risk_params
            )
            
            # Debug información de señales
            if hasattr(strategy, 'debug_info') and strategy.debug_info:
                with st.expander(f"{get_icon('debug')} 🔍 Debug Info - Análisis de Señales", expanded=False):
                    debug_info = strategy.debug_info[-15:]  # Últimas 15 entradas
                    for info in debug_info:
                        if info['type'] == 'signal':
                            signal_color = "🟢" if info['signal_type'] == 'BUY' else "🔴"
                            st.success(f"{signal_color} **{info['signal_type']}** - {info['timestamp']} | Precio: ${info['price']:.4f} | Confianza: {info['confidence']:.2%}")
                            st.code(f"Razón: {info['reason']}")
                        elif info['type'] == 'analysis':
                            st.info(f"📊 **Análisis** - {info['timestamp']} | Precio: ${info['price']:.4f}")
                            st.code(f"EMAs: Fast={info.get('ema_fast', 0):.4f}, Med={info.get('ema_medium', 0):.4f}, Slow={info.get('ema_slow', 0):.4f}")
                            st.code(f"Alineación: Bull={info.get('bullish', False)}, Bear={info.get('bearish', False)}, Posición={info.get('position', 'None')}")
                            if 'cross_info' in info:
                                st.code(f"Cruce detectado: {info['cross_info']}")
            
            # Información detallada de trades ejecutados
            if len(results.trades) > 0:
                with st.expander(f"{get_icon('trades')} 📊 Trades Ejecutados - Detalle de Señales", expanded=False):
                    st.info(f"Total de trades: {len(results.trades)} | Verifique que las señales aparezcan en los momentos correctos del gráfico")
                    
                    for i, trade in enumerate(results.trades[:8]):  # Mostrar primeros 8 trades
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            side_emoji = "🟢 ▲" if trade.side.lower() == 'long' else "🔴 ▼"
                            st.write(f"**{side_emoji} Trade #{i+1}**")
                            st.write(f"Tipo: **{trade.side.upper()}**")
                        with col2:
                            st.write(f"**📅 Entrada**")
                            st.write(f"{trade.entry_time.strftime('%m/%d %H:%M')}")
                            st.write(f"**${trade.entry_price:.4f}**")
                        with col3:
                            if trade.exit_time and trade.exit_price:
                                st.write(f"**🏁 Salida**")
                                st.write(f"{trade.exit_time.strftime('%m/%d %H:%M')}")
                                st.write(f"**${trade.exit_price:.4f}**")
                            else:
                                st.write("**⏳ Abierto**")
                        with col4:
                            if trade.pnl is not None:
                                pnl_emoji = "💚 +" if trade.pnl > 0 else "❌ -"
                                pnl_pct = ((trade.exit_price / trade.entry_price - 1) * 100) if trade.exit_price else 0
                                st.write(f"**📊 P&L**")
                                st.write(f"{pnl_emoji}${abs(trade.pnl):.2f}")
                                st.write(f"({pnl_pct:+.1f}%)")
                        
                        st.divider()
                    
                    if len(results.trades) > 8:
                        st.info(f"Mostrando primeros 8 de {len(results.trades)} trades totales")
            
            # Mostrar información de trades generados
            st.success(f"📊 **Análisis Completo:** {len(results.trades)} trades ejecutados | Señales visibles en el gráfico")
            
            # Guardar resultados en session state
            st.session_state.results = results
            st.session_state.strategy_name = strategy.get_strategy_name()
            st.session_state.symbol = symbol
            st.session_state.use_real_data = use_real_data  # Guardar configuración de datos
            
            st.success("✅ Backtest completado exitosamente!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error ejecutando backtest: {str(e)}")


def show_results():
    results = st.session_state.results
    strategy_name = st.session_state.strategy_name
    symbol = st.session_state.symbol
    
    st.header(f"{get_icon('chart')} Resultados: {strategy_name}")
    st.markdown(f"**Símbolo:** {symbol}")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        profit_color = "profit" if results.total_return > 0 else "loss"
        st.markdown(f"""
        <div class="metric-card">
            <h4>{get_icon('dollar')} Retorno Total</h4>
            <h2 class="{profit_color}">{format_currency(results.total_return)}</h2>
            <p class="{profit_color}">({format_percentage(results.total_return_pct)})</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{get_icon('trending')} Sharpe Ratio</h4>
            <h2>{results.sharpe_ratio:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📉 Max Drawdown</h4>
            <h2 class="loss">{format_percentage(results.max_drawdown_pct)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        win_color = "profit" if results.win_rate > 0.5 else "loss"
        st.markdown(f"""
        <div class="metric-card">
            <h4>🎯 Win Rate</h4>
            <h2 class="{win_color}">{format_percentage(results.win_rate)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"{get_icon('chart')} Curva de Equity")
        
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=results.equity_curve.index,
            y=results.equity_curve.values,
            mode='lines',
            name='Equity',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig_equity.add_hline(
            y=results.initial_capital,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Capital Inicial: {format_currency(results.initial_capital)}"
        )
        
        fig_equity.update_layout(
            height=400,
            xaxis_title="Fecha",
            yaxis_title="Equity ($)",
            showlegend=False
        )
        
        st.plotly_chart(fig_equity, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribución de Trades")
        
        if results.trades:
            closed_trades = [t for t in results.trades if not t.is_open and t.pnl is not None]
            if closed_trades:
                pnl_values = [t.pnl for t in closed_trades]
                
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Histogram(
                    x=pnl_values,
                    nbinsx=20,
                    marker_color='lightblue',
                    opacity=0.7
                ))
                
                fig_hist.update_layout(
                    height=400,
                    xaxis_title="PnL ($)",
                    yaxis_title="Frecuencia",
                    showlegend=False
                )
                
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("No hay trades cerrados para mostrar")
        else:
            st.info("No se ejecutaron trades")
    
    # Gráfico de señales de trading con indicadores
    st.subheader("🎯 Señales de Trading y Precios")
    
    # Mostrar información de debug
    with st.expander(f"{get_icon('search')} Información del Gráfico"):
        st.write(f"**Estrategia**: {strategy_name}")
        st.write(f"**Símbolo**: {symbol}")
        st.write(f"**Total trades**: {len(results.trades)}")
        closed_trades = [t for t in results.trades if not t.is_open]
        st.write(f"**Trades cerrados**: {len(closed_trades)}")
        if closed_trades:
            st.write(f"**Rango temporal**: {closed_trades[0].entry_time} - {closed_trades[-1].entry_time}")
    
    show_trading_signals_chart(results, strategy_name, symbol)
    
    # Drawdown
    st.subheader("📉 Drawdown")
    
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=results.drawdown_series.index,
        y=results.drawdown_series.values * 100,
        mode='lines',
        fill='tonexty',
        name='Drawdown %',
        line=dict(color='red', width=1),
        fillcolor='rgba(255, 0, 0, 0.3)'
    ))
    
    fig_dd.update_layout(
        height=300,
        xaxis_title="Fecha",
        yaxis_title="Drawdown (%)",
        showlegend=False
    )
    
    st.plotly_chart(fig_dd, use_container_width=True)
    
    # Tabla de métricas detalladas
    st.subheader("📋 Métricas Detalladas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        metrics_data = {
            "Métrica": [
                "Capital Inicial",
                "Capital Final", 
                "Retorno Total",
                "Retorno %",
                "Total Trades",
                "Trades Ganadores"
            ],
            "Valor": [
                format_currency(results.initial_capital),
                format_currency(results.final_capital),
                format_currency(results.total_return),
                format_percentage(results.total_return_pct),
                str(results.total_trades),  # Convertir a string
                str(results.winning_trades)  # Convertir a string
            ]
        }
        st.dataframe(pd.DataFrame(metrics_data), width="stretch")
    
    with col2:
        metrics_data2 = {
            "Métrica": [
                "Trades Perdedores",
                "Win Rate",
                "Ganancia Promedio",
                "Pérdida Promedio", 
                "Profit Factor",
                "Calmar Ratio"
            ],
            "Valor": [
                str(results.losing_trades),  # Convertir a string
                format_percentage(results.win_rate),
                format_currency(results.avg_win),
                format_currency(results.avg_loss),
                f"{results.profit_factor:.2f}",
                f"{results.calmar_ratio:.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(metrics_data2), width="stretch")
    
    # Botón para nuevo backtest
    if st.button("🔄 Ejecutar Nuevo Backtest", use_container_width=False):
        del st.session_state.results
        st.rerun()


def show_trading_signals_chart(results, strategy_name, symbol):
    """Muestra gráficos avanzados con máximo control y claridad"""
    if not results.trades:
        st.info("📊 No hay trades para mostrar en el gráfico")
        return
    
    try:
        # Controles de configuración del gráfico
        st.markdown("### ⚙️ Configuración del Gráfico")
        
        # Selector de tipo de gráfico
        chart_type = st.radio(
            "📊 Tipo de Gráfico:",
            ["TradingView Style", "Plotly Profesional", "Plotly Avanzado"],
            index=1,  # Plotly Profesional por defecto
            horizontal=True,
            help="📊 TradingView: Gráfico web interactivo | 📈 Plotly Pro: Estilo TradingView offline | 📊 Plotly Avanzado: Análisis multi-panel"
        )
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            show_volume = st.checkbox("📊 Mostrar Volumen", value=True)
        with col2:
            show_trade_lines = st.checkbox("🔗 Líneas de Trades", value=True)
        with col3:
            show_levels = st.checkbox("📏 Niveles S/R", value=True)
        with col4:
            chart_style = st.selectbox("🎨 Estilo", ["professional", "minimal", "detailed"], index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            timeframe = st.selectbox("⏱️ Timeframe", ["1h", "4h", "1d"], index=0)
        with col2:
            data_source = st.radio("📡 Fuente de Datos", 
                                 ["Automático", "Sintético", "Real"], 
                                 index=0, horizontal=True)
        
        # Configuración de datos
        use_real_data = st.session_state.get('use_real_data', False)
        
        if data_source == "Real":
            use_real_data = True
        elif data_source == "Sintético":
            use_real_data = False
        # "Automático" usa la configuración guardada
        
        # Crear cliente con la configuración seleccionada
        try:
            if use_real_data:
                client = BingXClient(use_synthetic=False)
                st.success("📡 Conectado a BingX API (datos reales)")
            else:
                client = BingXClient(use_synthetic=True)
                st.success("🎲 Usando generador sintético")
        except Exception as e:
            st.warning(f"⚠️ Error con API real: {e}. Usando datos sintéticos.")
            client = BingXClient(use_synthetic=True)
            use_real_data = False
        
        # Obtener rango de fechas de los trades
        first_trade = min(results.trades, key=lambda x: x.entry_time)
        last_trade = max(results.trades, key=lambda x: x.entry_time if x.entry_time else first_trade.entry_time)
        
        # Expandir rango para mejor contexto visual
        from datetime import timedelta
        start_date = (first_trade.entry_time - timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (last_trade.entry_time + timedelta(days=1)).strftime('%Y-%m-%d') if last_trade.entry_time else first_trade.entry_time.strftime('%Y-%m-%d')
        
        with st.spinner('📊 Generando gráfico avanzado...'):
            # Obtener datos históricos
            data = client.get_historical_data(
                symbol=symbol,
                interval=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            if data.empty:
                st.error("❌ No se pudieron obtener datos para el gráfico")
                return
            
            # Crear gráfico con el generador avanzado
            from src.visualization.advanced_charts import AdvancedChartGenerator
            generator = AdvancedChartGenerator()
            
            # Calcular indicadores básicos para el gráfico
            indicators = {}
            if 'ema' in strategy_name.lower() or 'triple' in strategy_name.lower():
                # Agregar EMAs comunes
                data['ema_20'] = data['close'].ewm(span=20).mean()
                data['ema_55'] = data['close'].ewm(span=55).mean() 
                data['ema_200'] = data['close'].ewm(span=200).mean()
                indicators = {
                    'ema_20': data['ema_20'],
                    'ema_55': data['ema_55'],
                    'ema_200': data['ema_200']
                }
            
            if 'rsi' in strategy_name.lower():
                # Calcular RSI
                delta = data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                data['rsi'] = 100 - (100 / (1 + rs))
                indicators['rsi'] = data['rsi']
            
            # Renderizar gráfico según el tipo seleccionado
            if chart_type == "TradingView Style":
                # Intentar usar TradingView Chart mejorado
                try:
                    create_enhanced_tradingview_chart(
                        data=data,
                        trades=results.trades,
                        indicators=indicators,
                        symbol=symbol
                    )
                except Exception as e:
                    st.error(f"Error con TradingView: {str(e)}")
                    st.info("🔄 Usando gráfico de fallback...")
                    create_fallback_chart(
                        data=data,
                        trades=results.trades,
                        indicators=indicators,
                        symbol=symbol
                    )
            elif chart_type == "Plotly Profesional":
                # Usar Plotly Profesional (estilo TradingView)
                create_professional_plotly_chart(
                    data=data,
                    trades=results.trades,
                    indicators=indicators,
                    symbol=symbol
                )
            else:
                # Usar Plotly Avanzado
                from src.visualization.advanced_charts import AdvancedChartGenerator
                generator = AdvancedChartGenerator()
                
                # Crear el gráfico profesional
                fig = generator.create_professional_trading_chart(
                    data=data,
                    trades=results.trades,
                    indicators=indicators,
                    symbol=symbol,
                    timeframe=timeframe,
                    show_volume=show_volume,
                    show_trade_lines=show_trade_lines,
                    show_levels=show_levels,
                    chart_style=chart_style
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Información del gráfico generado
            with st.expander(f"{get_icon('chart')} Detalles del Gráfico"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(f"{get_icon('chart')} Datos OHLC", len(data))
                    st.metric(f"{get_icon('target')} Total Trades", len(results.trades))
                with col2:
                    long_trades = len([t for t in results.trades if t.side.lower() == 'long'])
                    short_trades = len([t for t in results.trades if t.side.lower() == 'short'])
                    st.metric(f"{get_icon('green')} Long Trades", long_trades)
                    st.metric(f"{get_icon('red')} Short Trades", short_trades)
                with col3:
                    st.metric(f"{get_icon('time')} Timeframe", timeframe.upper())
                    if chart_type == "TradingView Style":
                        chart_display = "📊 TradingView"
                    elif chart_type == "Plotly Profesional":
                        chart_display = "📈 Plotly Pro"
                    else:
                        chart_display = "� Plotly Avanzado"
                    st.metric(f"{get_icon('chart')} Tipo Gráfico", chart_display)
                
                # Mostrar rango de datos
                st.info(f"{get_icon('calendar')} Rango: {data.index[0].strftime('%Y-%m-%d %H:%M')} → {data.index[-1].strftime('%Y-%m-%d %H:%M')}")
                
                # Información específica según tipo de gráfico
                if chart_type == "TradingView Style":
                    st.success("🎯 **TradingView:** Gráfico profesional con candlesticks interactivos, zoom avanzado y herramientas de trading integradas.")
                elif chart_type == "Plotly Profesional":
                    st.success("📈 **Plotly Profesional:** Gráfico estilo TradingView usando Plotly, completamente offline con señales y análisis profesional.")
                else:
                    st.success("📊 **Plotly Avanzado:** Gráfico multi-panel con análisis técnico detallado y métricas de performance.")
        
        # Gráfico de análisis de performance
        st.markdown(f"### {get_icon('trending')} Análisis de Performance")
        
        chart_generator = ChartGenerator()
        performance_fig = chart_generator.plot_trade_analysis(results, data)
        st.plotly_chart(performance_fig, use_container_width=True)
        
        # Controles adicionales
        with st.expander(f"{get_icon('tool')} Controles Avanzados"):
            st.markdown("**Opciones de Visualización:**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("""
                **🎯 Marcadores de Señales:**
                - 🟢 Triángulo Verde ↑: Long Entry
                - 🔴 Triángulo Rojo ↓: Long Exit  
                - 🔴 Triángulo Rojo ↓: Short Entry
                - 🟢 Triángulo Verde ↑: Short Exit
                """)
            
            with col2:
                st.info("""
                **📊 Líneas de Conexión:**
                - Verde Sólida: Trade Profitable
                - Roja Punteada: Trade con Pérdida
                - Grosor = Magnitud del P&L
                - Hover para detalles completos
                """)
            
            st.markdown("**🎨 Personalización:**")
            st.markdown("- Usa zoom y pan para explorar el gráfico")
            st.markdown("- Haz hover sobre elementos para información detallada") 
            st.markdown("- La leyenda es interactiva (clic para ocultar/mostrar)")
            st.markdown("- Usa los controles superiores para cambiar la visualización")
            
    except Exception as e:
        st.error(f"❌ Error generando gráfico: {str(e)}")
        st.info(f"{get_icon('info')} Intenta cambiar el timeframe o la fuente de datos")
        
        # Tabs para diferentes vistas
        tab1, tab2 = st.tabs(["📊 Análisis Detallado", "🎯 Vista Simple"])
        
        with tab1:
            st.markdown("**Gráfico con todas las señales, indicadores y análisis de performance**")
            
            # Preparar indicadores si es necesario
            indicators = {}
            
            # Para estrategias EMA, agregar las EMAs
            if "EMA" in strategy_name:
                from src.indicators.technical import TechnicalIndicators
                tech_indicators = TechnicalIndicators()
                
                if "Triple" in strategy_name:
                    indicators['ema_20'] = tech_indicators.ema(data['close'], period=20)
                    indicators['ema_55'] = tech_indicators.ema(data['close'], period=55)
                    indicators['ema_200'] = tech_indicators.ema(data['close'], period=200)
                elif "Golden Cross" in strategy_name:
                    indicators['ema_fast'] = tech_indicators.ema(data['close'], period=50)
                    indicators['ema_slow'] = tech_indicators.ema(data['close'], period=200)
            
            # Para RSI strategy
            elif "RSI" in strategy_name:
                from src.indicators.technical import TechnicalIndicators
                tech_indicators = TechnicalIndicators()
                indicators['rsi'] = tech_indicators.rsi(data['close'], period=14)
            
            # Para MACD strategy
            elif "MACD" in strategy_name:
                from src.indicators.technical import TechnicalIndicators
                tech_indicators = TechnicalIndicators()
                macd_line, macd_signal, macd_histogram = tech_indicators.macd(
                    data['close'], fast_period=12, slow_period=26, signal_period=9
                )
                indicators['macd'] = macd_line
                indicators['macd_signal'] = macd_signal
                indicators['macd_histogram'] = macd_histogram
            
            # Para Bollinger Bands
            elif "Bollinger" in strategy_name:
                from src.indicators.technical import TechnicalIndicators
                tech_indicators = TechnicalIndicators()
                bb_upper, bb_middle, bb_lower = tech_indicators.bollinger_bands(
                    data['close'], period=20, std_dev=2
                )
                indicators['bb_upper'] = bb_upper
                indicators['bb_middle'] = bb_middle
                indicators['bb_lower'] = bb_lower
            
            # Generar gráfico avanzado
            fig_advanced = chart_generator.plot_trading_signals_advanced(
                data=data,
                trades=results.trades,
                indicators=indicators,
                symbol=symbol,
                title=f"{strategy_name} - {symbol}"
            )
            
            st.plotly_chart(fig_advanced, use_container_width=True)
        
        with tab2:
            st.markdown("**Vista simplificada mostrando solo ganadores vs perdedores**")
            
            # Gráfico de análisis simple
            fig_simple = chart_generator.plot_trade_analysis(
                data=data,
                trades=results.trades,
                symbol=symbol
            )
            
            st.plotly_chart(fig_simple, use_container_width=True)
            
        # Estadísticas de trades
        st.markdown("### � Estadísticas de Trades")
        
        closed_trades = [t for t in results.trades if not t.is_open]
        if closed_trades:
            long_trades = [t for t in closed_trades if t.side.lower() == 'long']
            short_trades = [t for t in closed_trades if t.side.lower() == 'short']
            
            winning_longs = [t for t in long_trades if t.pnl > 0]
            losing_longs = [t for t in long_trades if t.pnl <= 0]
            winning_shorts = [t for t in short_trades if t.pnl > 0]
            losing_shorts = [t for t in short_trades if t.pnl <= 0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🟢 Longs Ganadores",
                    value=len(winning_longs),
                    delta=f"{len(winning_longs)/max(len(long_trades), 1)*100:.1f}%" if long_trades else "0%"
                )
            
            with col2:
                st.metric(
                    label="🔴 Longs Perdedores", 
                    value=len(losing_longs),
                    delta=f"-{len(losing_longs)/max(len(long_trades), 1)*100:.1f}%" if long_trades else "0%"
                )
            
            with col3:
                st.metric(
                    label="🟠 Shorts Ganadores",
                    value=len(winning_shorts),
                    delta=f"{len(winning_shorts)/max(len(short_trades), 1)*100:.1f}%" if short_trades else "0%"
                )
            
            with col4:
                st.metric(
                    label="🔴 Shorts Perdedores",
                    value=len(losing_shorts), 
                    delta=f"-{len(losing_shorts)/max(len(short_trades), 1)*100:.1f}%" if short_trades else "0%"
                )
            
            # Tabla resumen de trades
            if st.checkbox("📊 Mostrar Detalle de Trades"):
                trades_data = []
                for i, trade in enumerate(closed_trades[-10:], 1):  # Últimos 10 trades
                    trades_data.append({
                        '#': i,
                        'Tipo': '🟢 Long' if trade.side.lower() == 'long' else '🔴 Short',
                        'Entrada': trade.entry_time.strftime('%Y-%m-%d %H:%M') if trade.entry_time else 'N/A',
                        'Precio Entrada': f"${trade.entry_price:.4f}",
                        'Salida': trade.exit_time.strftime('%Y-%m-%d %H:%M') if trade.exit_time else 'Abierto',
                        'Precio Salida': f"${trade.exit_price:.4f}" if trade.exit_price else 'N/A',
                        'P&L': f"${trade.pnl:.2f}" if trade.pnl else 'N/A',
                        'Resultado': '✅ Ganador' if trade.pnl and trade.pnl > 0 else '❌ Perdedor' if trade.pnl else '⏳ Abierto'
                    })
                
                st.dataframe(pd.DataFrame(trades_data), width="stretch")
        
    except Exception as e:
        st.error(f"❌ Error generando gráfico: {str(e)}")
        
        # Mostrar información de debug
        with st.expander(f"{get_icon('debug')} Información de Debug"):
            st.code(f"Error: {str(e)}")
            st.write("**Parámetros del error:**")
            st.write(f"- Símbolo: {symbol}")
            st.write(f"- Estrategia: {strategy_name}")
            st.write(f"- Número de trades: {len(results.trades) if results.trades else 0}")
        
        st.info("🔧 Mostrando información básica de trades...")
        
        # Fallback: mostrar tabla simple de trades
        if results.trades:
            st.write(f"**Total de trades ejecutados:** {len(results.trades)}")
            closed_trades = [t for t in results.trades if not t.is_open]
            if closed_trades:
                winners = [t for t in closed_trades if t.pnl and t.pnl > 0]
                st.write(f"**Trades ganadores:** {len(winners)}")
                st.write(f"**Win Rate:** {len(winners)/len(closed_trades)*100:.1f}%")
                
                # Mostrar algunos trades de ejemplo
                if len(closed_trades) > 0:
                    st.write("**Últimos 5 trades:**")
                    for i, trade in enumerate(closed_trades[-5:], 1):
                        side = "🟢 LONG" if trade.side.lower() == 'long' else "🔴 SHORT"
                        result = "✅" if trade.pnl and trade.pnl > 0 else "❌"
                        pnl_str = f"${trade.pnl:.2f}" if trade.pnl else "N/A"
                        st.write(f"{i}. {side} {result} P&L: {pnl_str}")
        else:
            st.info("📊 No hay trades para mostrar")


if __name__ == "__main__":
    main()