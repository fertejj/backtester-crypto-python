# Contribuir al Crypto Trading Backtester

¡Gracias por tu interés en contribuir! 🎉

## 🚀 Cómo Contribuir

### 1. Fork y Clone
```bash
git fork https://github.com/[tu-usuario]/backtester-cripto
git clone https://github.com/[tu-usuario]/backtester-cripto.git
cd backtester-cripto
```

### 2. Configurar Entorno
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Crear Branch
```bash
git checkout -b feature/nueva-estrategia
```

## 🔧 Desarrollo

### Estructura del Código
- `src/strategies/`: Nuevas estrategias de trading
- `src/indicators/`: Indicadores técnicos
- `src/api/`: Clientes de APIs
- `tests/`: Tests unitarios (obligatorio)

### Estándares de Código
- Usa `black` para formatear: `black src/ tests/`
- Verifica con `flake8`: `flake8 src/ tests/`
- Ejecuta tests: `pytest tests/ -v`

### Nuevas Estrategias
Para agregar una nueva estrategia:

1. Crea archivo en `src/strategies/mi_estrategia.py`
2. Hereda de `BaseStrategy`
3. Implementa `should_buy()` y `should_sell()`
4. Agrega tests en `tests/test_mi_estrategia.py`
5. Actualiza `app.py` para incluir en la UI

Ejemplo:
```python
from src.strategies.base import BaseStrategy

class MiEstrategia(BaseStrategy):
    def should_buy(self, data, current_price, position):
        # Tu lógica aquí
        return True, "Señal de compra"
    
    def should_sell(self, data, current_price, position):
        # Tu lógica aquí
        return True, "Señal de venta"
```

## 📋 Pull Request

1. Asegúrate que todos los tests pasen
2. Actualiza documentación si es necesario
3. Describe claramente los cambios
4. Incluye screenshots si afecta la UI

## 🐛 Reportar Bugs

Usa el template de issues con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Versión de Python y dependencias

## 💡 Sugerir Funcionalidades

- Abre un issue con etiqueta `enhancement`
- Describe el caso de uso
- Incluye mockups si es UI
- Discute implementación antes de codificar

## 📞 Contacto

- Issues: Para bugs y sugerencias
- Discussions: Para preguntas generales
- Email: [tu-email] para temas privados

¡Toda contribución es bienvenida! 🙌