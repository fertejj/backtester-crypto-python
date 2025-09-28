import streamlit as st
import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.backtester.metrics import BacktestResults, Trade


class TradingViewChart:
    """Generador de gráficos estilo TradingView usando lightweight-charts"""
    
    def __init__(self):
        self.chart_id = "trading_chart"
        
    def create_tradingview_chart(self, 
                                data: pd.DataFrame, 
                                trades: List[Trade],
                                symbol: str = "CRYPTO",
                                indicators: Optional[Dict] = None,
                                height: int = 600) -> str:
        """
        Crea un gráfico estilo TradingView con lightweight-charts
        
        Args:
            data: DataFrame con datos OHLCV
            trades: Lista de trades ejecutados
            symbol: Símbolo del activo
            indicators: Indicadores técnicos opcionales
            height: Altura del gráfico
            
        Returns:
            HTML string con el gráfico TradingView
        """
        
        # Preparar datos OHLCV para TradingView
        ohlc_data = self._prepare_ohlcv_data(data)
        
        # Preparar datos de volumen
        volume_data = self._prepare_volume_data(data)
        
        # Preparar señales de trading
        signals_data = self._prepare_signals_data(trades)
        
        # Preparar indicadores
        indicators_data = self._prepare_indicators_data(data, indicators) if indicators else {}
        
        # Generar HTML del gráfico
        chart_html = self._generate_chart_html(
            ohlc_data, volume_data, signals_data, indicators_data, 
            symbol, height
        )
        
        return chart_html
    
    def _prepare_ohlcv_data(self, data: pd.DataFrame) -> List[Dict]:
        """Prepara datos OHLCV para el gráfico"""
        ohlc_list = []
        
        for idx, row in data.iterrows():
            # TradingView requiere timestamp en formato YYYY-MM-DD o timestamp unix
            if hasattr(idx, 'strftime'):
                time_value = idx.strftime('%Y-%m-%d')
                if hasattr(idx, 'hour'):  # Si tiene hora, usar formato completo
                    time_value = idx.strftime('%Y-%m-%d %H:%M')
            else:
                time_value = int(idx.timestamp()) if hasattr(idx, 'timestamp') else int(datetime.now().timestamp())
            
            ohlc_list.append({
                'time': time_value,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
            
        return ohlc_list
    
    def _prepare_volume_data(self, data: pd.DataFrame) -> List[Dict]:
        """Prepara datos de volumen"""
        volume_list = []
        
        if 'volume' not in data.columns:
            return volume_list
            
        for idx, row in data.iterrows():
            # TradingView requiere timestamp en formato YYYY-MM-DD o timestamp unix
            if hasattr(idx, 'strftime'):
                time_value = idx.strftime('%Y-%m-%d')
                if hasattr(idx, 'hour'):  # Si tiene hora, usar formato completo
                    time_value = idx.strftime('%Y-%m-%d %H:%M')
            else:
                time_value = int(idx.timestamp()) if hasattr(idx, 'timestamp') else int(datetime.now().timestamp())
            
            # Color basado en dirección del precio
            color = '#00C896' if row['close'] >= row['open'] else '#FF4B4B'
            
            volume_list.append({
                'time': time_value,
                'value': float(row['volume']),
                'color': color
            })
            
        return volume_list
    
    def _prepare_signals_data(self, trades: List[Trade]) -> Dict[str, List[Dict]]:
        """Prepara señales de trading para el gráfico"""
        long_entries = []
        long_exits = []
        short_entries = []
        short_exits = []
        
        for trade in trades:
            if trade.entry_time:
                # Formato de tiempo para TradingView
                if hasattr(trade.entry_time, 'strftime'):
                    entry_time = trade.entry_time.strftime('%Y-%m-%d')
                    if hasattr(trade.entry_time, 'hour'):
                        entry_time = trade.entry_time.strftime('%Y-%m-%d %H:%M')
                else:
                    entry_time = int(trade.entry_time.timestamp())
                
                signal_data = {
                    'time': entry_time,
                    'position': 'belowBar' if trade.side.lower() == 'long' else 'aboveBar',
                    'color': '#00E676' if trade.side.lower() == 'long' else '#FF5722',
                    'shape': 'arrowUp' if trade.side.lower() == 'long' else 'arrowDown',
                    'text': f"{'🟢 LONG' if trade.side.lower() == 'long' else '🔴 SHORT'} ${trade.entry_price:.4f}"
                }
                
                if trade.side.lower() == 'long':
                    long_entries.append(signal_data)
                else:
                    short_entries.append(signal_data)
            
            if trade.exit_time and trade.exit_price:
                # Formato de tiempo para TradingView
                if hasattr(trade.exit_time, 'strftime'):
                    exit_time = trade.exit_time.strftime('%Y-%m-%d')
                    if hasattr(trade.exit_time, 'hour'):
                        exit_time = trade.exit_time.strftime('%Y-%m-%d %H:%M')
                else:
                    exit_time = int(trade.exit_time.timestamp())
                
                exit_signal = {
                    'time': exit_time,
                    'position': 'aboveBar' if trade.side.lower() == 'long' else 'belowBar',
                    'color': '#4CAF50' if trade.pnl > 0 else '#F44336',
                    'shape': 'arrowDown' if trade.side.lower() == 'long' else 'arrowUp',
                    'text': f"EXIT ${trade.exit_price:.4f} | P&L: ${trade.pnl:.2f}"
                }
                
                if trade.side.lower() == 'long':
                    long_exits.append(exit_signal)
                else:
                    short_exits.append(exit_signal)
        
        return {
            'long_entries': long_entries,
            'long_exits': long_exits,
            'short_entries': short_entries,
            'short_exits': short_exits
        }
    
    def _prepare_indicators_data(self, data: pd.DataFrame, indicators: Dict) -> Dict[str, List[Dict]]:
        """Prepara datos de indicadores técnicos"""
        indicators_data = {}
        
        for key, values in indicators.items():
            if values is not None and len(values) > 0:
                indicator_list = []
                
                for idx, value in zip(data.index, values):
                    if pd.notna(value):
                        # Formato de tiempo para TradingView
                        if hasattr(idx, 'strftime'):
                            time_value = idx.strftime('%Y-%m-%d')
                            if hasattr(idx, 'hour'):  # Si tiene hora, usar formato completo
                                time_value = idx.strftime('%Y-%m-%d %H:%M')
                        else:
                            time_value = int(idx.timestamp()) if hasattr(idx, 'timestamp') else int(datetime.now().timestamp())
                        
                        indicator_list.append({
                            'time': time_value,
                            'value': float(value)
                        })
                
                indicators_data[key] = indicator_list
        
        return indicators_data
    
    def _generate_chart_html(self, ohlc_data: List[Dict], volume_data: List[Dict], 
                           signals_data: Dict, indicators_data: Dict, 
                           symbol: str, height: int) -> str:
        """Genera el HTML del gráfico TradingView"""
        
        # Validar que hay datos
        if not ohlc_data or len(ohlc_data) == 0:
            return f"""
            <div style="height: {height}px; display: flex; align-items: center; justify-content: center; border: 1px solid #ccc; background: #f5f5f5;">
                <h3 style="color: #666;">⚠️ No hay datos disponibles para mostrar el gráfico TradingView</h3>
            </div>
            """
        
        html_template = f"""
        <div id="{self.chart_id}" style="height: {height}px; width: 100%; border: 1px solid #e0e0e0; border-radius: 8px;"></div>
        
        <!-- TradingView Lightweight Charts Library -->
        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
        
        <script>
            try {{
                console.log('Iniciando TradingView Chart...');
                console.log('Datos OHLC:', {json.dumps(ohlc_data[:5])});
                
                // Crear el gráfico
                const chart = LightweightCharts.createChart(document.getElementById('{self.chart_id}'), {{
                    width: document.getElementById('{self.chart_id}').clientWidth,
                    height: {height - 10},
                    layout: {{
                        backgroundColor: '#ffffff',
                        textColor: '#333333',
                        fontSize: 12,
                        fontFamily: 'Arial, sans-serif'
                    }},
                    grid: {{
                        vertLines: {{
                            color: '#f0f0f0',
                            style: 1,
                            visible: true,
                        }},
                        horzLines: {{
                            color: '#f0f0f0',
                            style: 1,
                            visible: true,
                        }},
                    }},
                    crosshair: {{
                        mode: LightweightCharts.CrosshairMode.Normal,
                    }},
                    rightPriceScale: {{
                        borderColor: '#cccccc',
                        scaleMargins: {{
                            top: 0.1,
                            bottom: 0.2,
                        }},
                    }},
                    timeScale: {{
                        borderColor: '#cccccc',
                        timeVisible: true,
                        secondsVisible: false,
                    }},
                }});
                
                // Serie de candlesticks principal
                const candleSeries = chart.addCandlestickSeries({{
                    upColor: '#00C896',
                    downColor: '#FF4B4B',
                    borderDownColor: '#FF4B4B',
                    borderUpColor: '#00C896',
                    wickDownColor: '#FF4B4B',
                    wickUpColor: '#00C896',
                    priceFormat: {{
                        type: 'price',
                        precision: 4,
                        minMove: 0.0001,
                    }},
                }});
                
                // Datos OHLC
                console.log('Cargando datos OHLC...');
                candleSeries.setData({json.dumps(ohlc_data)});
                console.log('Datos OHLC cargados exitosamente');"""
        
        # Agregar volumen si hay datos
        if volume_data and len(volume_data) > 0:
            html_template += f"""
                
                // Serie de volumen
                console.log('Cargando datos de volumen...');
                const volumeSeries = chart.addHistogramSeries({{
                    color: '#26a69a',
                    priceFormat: {{
                        type: 'volume',
                    }},
                    priceScaleId: '',
                    scaleMargins: {{
                        top: 0.8,
                        bottom: 0,
                    }},
                }});
                
                // Datos de volumen
                volumeSeries.setData({json.dumps(volume_data)});
                console.log('Datos de volumen cargados exitosamente');"""
        
        # Agregar indicadores
        indicator_colors = {
            'ema_20': '#FF9800',
            'ema_55': '#2196F3', 
            'ema_200': '#E91E63',
            'ema_fast': '#FF9800',
            'ema_medium': '#2196F3',
            'ema_slow': '#E91E63',
            'bb_upper': '#9C27B0',
            'bb_lower': '#9C27B0',
            'bb_middle': '#9C27B0'
        }
        
        for indicator_name, indicator_data in indicators_data.items():
            if indicator_data and len(indicator_data) > 0:
                color = indicator_colors.get(indicator_name, '#666666')
                line_width = 3 if '200' in indicator_name or 'slow' in indicator_name else 2
                
                html_template += f"""
                
                // Indicador: {indicator_name}
                console.log('Cargando indicador {indicator_name}...');
                const {indicator_name.replace('-', '_')}Series = chart.addLineSeries({{
                    color: '{color}',
                    lineWidth: {line_width},
                    title: '{indicator_name.upper()}',
                    lastValueVisible: true,
                    priceLineVisible: false,
                }});
                {indicator_name.replace('-', '_')}Series.setData({json.dumps(indicator_data)});
                console.log('Indicador {indicator_name} cargado exitosamente');"""
        
        # Agregar todas las señales como markers en la serie principal
        all_markers = []
        for signal_type, signals in signals_data.items():
            all_markers.extend(signals)
        
        if all_markers:
            html_template += f"""
            
            // Señales de trading
            console.log('Cargando señales de trading...');
            candleSeries.setMarkers({json.dumps(all_markers)});
            console.log('Señales cargadas exitosamente');"""
        
        # Finalizar el script
        html_template += f"""
                
                // Redimensionar automáticamente
                window.addEventListener('resize', () => {{
                    chart.applyOptions({{
                        width: document.getElementById('{self.chart_id}').clientWidth,
                    }});
                }});
                
                // Título del gráfico
                const title = document.createElement('div');
                title.innerHTML = '<h3 style="margin: 0; color: #333; font-family: Arial;">📊 {symbol} - TradingView Chart</h3>';
                title.style.position = 'absolute';
                title.style.top = '10px';
                title.style.left = '15px';
                title.style.zIndex = '1000';
                title.style.backgroundColor = 'rgba(255,255,255,0.9)';
                title.style.padding = '5px 10px';
                title.style.borderRadius = '5px';
                title.style.border = '1px solid #ddd';
                document.getElementById('{self.chart_id}').style.position = 'relative';
                document.getElementById('{self.chart_id}').appendChild(title);
                
                console.log('TradingView Chart inicializado exitosamente');
                
            }} catch (error) {{
                console.error('Error inicializando TradingView Chart:', error);
                document.getElementById('{self.chart_id}').innerHTML = 
                    '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #d32f2f; font-size: 16px;">' +
                    '❌ Error cargando gráfico TradingView: ' + error.message + 
                    '</div>';
            }}
        </script>
        </body>
        </html>
        """
        
        return html_template
            'ema_200': '#E91E63',
            'ema_fast': '#FF9800',
            'ema_slow': '#2196F3',
            'bb_upper': '#9C27B0',
            'bb_lower': '#9C27B0',
            'bb_middle': '#9C27B0'
        }
        
        for indicator_name, indicator_data in indicators_data.items():
            color = indicator_colors.get(indicator_name, '#666666')
            line_width = 3 if '200' in indicator_name else 2
            
            html_template += f"""
            // Indicador: {indicator_name}
            const {indicator_name}Series = chart.addLineSeries({{
                color: '{color}',
                lineWidth: {line_width},
                title: '{indicator_name.upper()}',
                lastValueVisible: true,
                priceLineVisible: true,
            }});
            {indicator_name}Series.setData({json.dumps(indicator_data)});
            """
        
        # Agregar señales de trading
        signals_colors = {
            'long_entries': '#00E676',
            'long_exits': '#4CAF50', 
            'short_entries': '#FF5722',
            'short_exits': '#FF8A65'
        }
        
        for signal_type, signals in signals_data.items():
            if signals:  # Solo agregar si hay señales
                html_template += f"""
                // Señales: {signal_type}
                candleSeries.setMarkers({json.dumps(signals)});
                """
        
        # Finalizar el script
        html_template += f"""
            // Redimensionar automáticamente
            window.addEventListener('resize', () => {{
                chart.applyOptions({{
                    width: document.getElementById('{self.chart_id}').clientWidth,
                }});
            }});
            
            // Título del gráfico
            const title = document.createElement('div');
            title.innerHTML = '<h3 style="margin: 0; color: #333; font-family: Roboto;">📊 {symbol} - Análisis Profesional de Trading</h3>';
            title.style.position = 'absolute';
            title.style.top = '10px';
            title.style.left = '10px';
            title.style.zIndex = '1000';
            title.style.backgroundColor = 'rgba(255,255,255,0.9)';
            title.style.padding = '5px 10px';
            title.style.borderRadius = '5px';
            document.getElementById('{self.chart_id}').style.position = 'relative';
            document.getElementById('{self.chart_id}').appendChild(title);
        </script>
        """
        
        return html_template


def create_tradingview_component(data: pd.DataFrame, trades: List[Trade], 
                               symbol: str = "CRYPTO", indicators: Optional[Dict] = None):
    """Función helper para crear el componente TradingView en Streamlit"""
    
    # Crear instancia del generador de gráficos
    tv_chart = TradingViewChart()
    
    # Generar HTML del gráfico
    chart_html = tv_chart.create_tradingview_chart(
        data=data,
        trades=trades,
        symbol=symbol,
        indicators=indicators,
        height=600
    )
    
    # Mostrar en Streamlit usando HTML
    st.components.v1.html(chart_html, height=650)