import streamlit as st
import pandas as pd
import json
from typing import List, Dict, Any, Optional
from src.backtester.metrics import Trade


def create_simple_tradingview_chart(data: pd.DataFrame, trades: List[Trade], 
                                   symbol: str = "CRYPTO", indicators: Optional[Dict] = None):
    """Función simplificada para crear gráfico TradingView"""
    
    # Debug: Mostrar información de los datos recibidos
    st.info(f"📊 **Debug TradingView:** {len(data)} barras de datos | {len(trades)} trades | Rango: {data.index[0]} → {data.index[-1]}")
    
    if len(data) == 0:
        st.error("❌ No hay datos para mostrar en el gráfico TradingView")
        return
    
    # Preparar datos OHLCV básicos
    ohlc_data = []
    for idx, row in data.iterrows():
        # Usar formato de fecha simple
        time_str = idx.strftime('%Y-%m-%d')
        if hasattr(idx, 'hour'):
            time_str = idx.strftime('%Y-%m-%d %H:%M')
            
        ohlc_data.append({
            'time': time_str,
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close'])
        })
    
    st.success(f"✅ Datos OHLC preparados: {len(ohlc_data)} puntos")
    
    # Preparar señales básicas
    markers = []
    for trade in trades:
        if trade.entry_time:
            time_str = trade.entry_time.strftime('%Y-%m-%d')
            if hasattr(trade.entry_time, 'hour'):
                time_str = trade.entry_time.strftime('%Y-%m-%d %H:%M')
                
            marker = {
                'time': time_str,
                'position': 'belowBar' if trade.side.lower() == 'long' else 'aboveBar',
                'color': '#00E676' if trade.side.lower() == 'long' else '#FF5722',
                'shape': 'arrowUp' if trade.side.lower() == 'long' else 'arrowDown',
                'text': f"{'🟢' if trade.side.lower() == 'long' else '🔴'} ${trade.entry_price:.4f}"
            }
            markers.append(marker)
    
    st.info(f"🎯 **Señales preparadas:** {len(markers)} marcadores de entrada")
    
    # HTML simplificado
    chart_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TradingView Chart</title>
    </head>
    <body style="margin: 0; padding: 10px; font-family: Arial, sans-serif;">
        <div id="tradingview-chart" style="height: 500px; width: 100%; border: 1px solid #ccc; background: #fafafa;">
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">
                📊 Cargando gráfico TradingView...
            </div>
        </div>
        
        <script>
            console.log('Iniciando carga de TradingView...');
            
            // Función para cargar el script
            function loadTradingView() {{
                return new Promise((resolve, reject) => {{
                    const script = document.createElement('script');
                    script.src = 'https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js';
                    script.onload = () => {{
                        console.log('TradingView script cargado exitosamente');
                        resolve();
                    }};
                    script.onerror = (error) => {{
                        console.error('Error cargando TradingView script:', error);
                        reject(error);
                    }};
                    document.head.appendChild(script);
                }});
            }}
            
            // Función principal para crear el gráfico
            async function createChart() {{
                try {{
                    // Cargar la librería
                    await loadTradingView();
                    
                    // Verificar que la librería esté disponible
                    if (typeof LightweightCharts === 'undefined') {{
                        throw new Error('LightweightCharts no está disponible');
                    }}
                    
                    console.log('Creando gráfico TradingView...');
                    console.log('LightweightCharts version:', LightweightCharts);
                    
                    const chartContainer = document.getElementById('tradingview-chart');
                    
                    const chart = LightweightCharts.createChart(chartContainer, {{
                        width: chartContainer.clientWidth,
                        height: 480,
                        layout: {{
                            background: {{
                                type: 'solid',
                                color: '#ffffff',
                            }},
                            textColor: '#333333',
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
                        timeScale: {{
                            timeVisible: true,
                            secondsVisible: false,
                            borderColor: '#cccccc',
                        }},
                        rightPriceScale: {{
                            borderColor: '#cccccc',
                        }},
                    }});
                    
                    // Verificar que el chart se creó correctamente
                    if (!chart || typeof chart.addCandlestickSeries !== 'function') {{
                        throw new Error('El objeto chart no tiene el método addCandlestickSeries');
                    }}
                    
                    console.log('Chart creado, añadiendo serie de candlesticks...');
                    
                    const candleSeries = chart.addCandlestickSeries({{
                        upColor: '#00C896',
                        downColor: '#FF4B4B',
                        borderDownColor: '#FF4B4B',
                        borderUpColor: '#00C896',
                        wickDownColor: '#FF4B4B',
                        wickUpColor: '#00C896',
                        priceFormat: {{
                            type: 'price',
                            precision: 2,
                            minMove: 0.01,
                        }},
                    }});
                    
                    // Datos principales
                    const ohlcData = {json.dumps(ohlc_data)};
                    console.log('Cargando', ohlcData.length, 'datos OHLC...');
                    console.log('Muestra de datos:', ohlcData.slice(0, 3));
                    
                    if (ohlcData.length === 0) {{
                        throw new Error('No hay datos OHLC para mostrar');
                    }}
                    
                    candleSeries.setData(ohlcData);
                    console.log('Datos OHLC cargados exitosamente');
                    
                    // Señales
                    const markers = {json.dumps(markers)};
                    if (markers.length > 0) {{
                        console.log('Añadiendo', markers.length, 'señales...');
                        candleSeries.setMarkers(markers);
                        console.log('Señales añadidas exitosamente');
                    }}
                    
                    // Título
                    const title = document.createElement('div');
                    title.innerHTML = '<h3 style="margin: 0; color: #333;">📊 {symbol} - TradingView Chart</h3>';
                    title.style.cssText = `
                        position: absolute; 
                        top: 15px; 
                        left: 20px; 
                        z-index: 1000; 
                        background: rgba(255,255,255,0.95); 
                        padding: 8px 15px; 
                        border-radius: 6px;
                        border: 1px solid #e0e0e0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    `;
                    chartContainer.style.position = 'relative';
                    chartContainer.appendChild(title);
                    
                    // Redimensionar automáticamente
                    window.addEventListener('resize', () => {{
                        chart.applyOptions({{
                            width: chartContainer.clientWidth,
                        }});
                    }});
                    
                    console.log('✅ TradingView Chart creado exitosamente');
                    
                }} catch (error) {{
                    console.error('❌ Error creando TradingView Chart:', error);
                    
                    const errorMsg = `
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; color: #d32f2f;">
                            <h3 style="margin: 0 0 10px 0;">❌ Error en TradingView Chart</h3>
                            <p style="margin: 0; background: #ffebee; padding: 10px; border-radius: 5px; border-left: 4px solid #d32f2f;">
                                ${{error.message}}
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                                Revisa la consola para más detalles
                            </p>
                        </div>
                    `;
                    
                    document.getElementById('tradingview-chart').innerHTML = errorMsg;
                }}
            }}
            
            // Ejecutar cuando el DOM esté listo
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', createChart);
            }} else {{
                createChart();
            }}
        </script>
    </body>
    </html>
    """
    
    # Mostrar en Streamlit
    st.components.v1.html(chart_html, height=550)
    st.success("✅ Gráfico TradingView cargado correctamente")