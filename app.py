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


# Configuración de la página
st.set_page_config(
    page_title="Crypto Trading Backtester",
    page_icon="📈",
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
    st.title("🚀 Crypto Trading Backtester")
    st.markdown("### Analiza y optimiza tus estrategias de trading de criptomonedas")

    # Sidebar - Configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Configuración del activo
        st.subheader("📊 Activo y Período")
        symbol = st.selectbox(
            "Símbolo:", 
            ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"],
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
        st.subheader("🎯 Estrategia")
        strategy_type = st.selectbox(
            "Tipo de Estrategia:",
            ["RSI", "MACD", "Bollinger Bands", "EMA Triple", "EMA Golden Cross"]
        )
        
        # Panel dinámico de parámetros según estrategia
        st.markdown("---")
        st.markdown("**⚙️ Parámetros de la Estrategia:**")
        
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
                    st.info(f"📊 Señal Compra: RSI < {buy_threshold} (Sobreventa)")
                    st.info(f"📊 Señal Venta: RSI > {sell_threshold} (Sobrecompra)")
            
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
                st.info("📊 Señales: Cruces de línea MACD con línea de señal")
            
        elif strategy_type == "Bollinger Bands":
            with st.container():
                st.markdown("*Bandas de Bollinger - Volatilidad*")
                col1, col2 = st.columns(2)
                with col1:
                    bb_period = st.slider("Período BB:", 10, 30, 20)
                with col2:
                    bb_std = st.slider("Desviación Estándar:", 1.5, 3.0, 2.0, 0.1)
                st.info("📊 Compra: Precio toca banda inferior | Venta: Precio toca banda superior")
            
        elif strategy_type == "EMA Triple":
            with st.container():
                st.markdown("*Triple EMA con filtros direccionales*")
                
                # Configuración de EMAs
                st.markdown("**📈 Configuración de EMAs:**")
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
                with st.expander("⚙️ Configuración Avanzada"):
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
                st.info("📊 Golden Cross: EMA rápida > EMA lenta | Death Cross: EMA rápida < EMA lenta")
        
        # Gestión de Riesgo
        st.subheader("⚖️ Gestión de Riesgo")
        max_position_size = st.slider("Tamaño Máx. Posición (%):", 5, 50, 20) / 100
        stop_loss_pct = st.slider("Stop Loss (%):", 0, 20, 5) / 100
        take_profit_pct = st.slider("Take Profit (%):", 0, 30, 10) / 100
        risk_per_trade = st.slider("Riesgo por Trade (%):", 1, 10, 2) / 100
        
        # Botón de ejecución
        if st.button("🚀 Ejecutar Backtest", type="primary", use_container_width=False):
            run_backtest(
                symbol, start_date, end_date, interval, initial_capital,
                strategy_type, locals(), max_position_size, stop_loss_pct,
                take_profit_pct, risk_per_trade
            )

    # Área principal
    if 'results' not in st.session_state:
        st.info("👈 Configura los parámetros en el panel lateral y haz clic en 'Ejecutar Backtest' para comenzar.")
        
        # Mostrar información del proyecto
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔧 Características:**
            - Múltiples estrategias de trading
            - Indicadores técnicos avanzados  
            - Gestión de riesgo integrada
            - Métricas de rendimiento detalladas
            """)
        
        with col2:
            st.markdown("""
            **📊 Estrategias Disponibles:**
            - RSI (Relative Strength Index)
            - MACD (Moving Average Convergence Divergence)
            - Bollinger Bands
            - EMA Triple (20/55/200 con filtros)
            - EMA Golden Cross (50/200)
            """)
        
        with col3:
            st.markdown("""
            **📈 Métricas Calculadas:**
            - Retorno total y anualizado
            - Sharpe Ratio
            - Maximum Drawdown
            - Win Rate y Profit Factor
            """)
    else:
        show_results()


def run_backtest(symbol, start_date, end_date, interval, initial_capital,
                strategy_type, params, max_position_size, stop_loss_pct,
                take_profit_pct, risk_per_trade):
    
    with st.spinner('🔄 Ejecutando backtest... Esto puede tomar unos segundos.'):
        try:
            # Crear cliente API (usará datos sintéticos si no está configurado)
            api_client = None
            
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
            
            # Guardar resultados en session state
            st.session_state.results = results
            st.session_state.strategy_name = strategy.get_strategy_name()
            st.session_state.symbol = symbol
            
            st.success("✅ Backtest completado exitosamente!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error ejecutando backtest: {str(e)}")


def show_results():
    results = st.session_state.results
    strategy_name = st.session_state.strategy_name
    symbol = st.session_state.symbol
    
    st.header(f"📊 Resultados: {strategy_name}")
    st.markdown(f"**Símbolo:** {symbol}")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        profit_color = "profit" if results.total_return > 0 else "loss"
        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 Retorno Total</h4>
            <h2 class="{profit_color}">{format_currency(results.total_return)}</h2>
            <p class="{profit_color}">({format_percentage(results.total_return_pct)})</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📈 Sharpe Ratio</h4>
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
        st.subheader("📈 Curva de Equity")
        
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
    """Muestra un gráfico con precios, indicadores y señales de trading"""
    # Esta función necesitaría acceso a los datos originales con indicadores
    # Por ahora mostramos un placeholder
    st.info("🚧 Gráfico de señales en desarrollo. Próximamente mostrará precios con indicadores y puntos de entrada/salida.")


if __name__ == "__main__":
    main()