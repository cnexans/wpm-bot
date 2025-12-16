# 🤖 WPM Bot - Bot de Escritura Automática para wpm.silver.dev

## 🎯 ¿Qué es esto?

Un bot automatizado que juega [wpm.silver.dev](https://wpm.silver.dev), un juego de mecanografía donde debes escribir código en lugar de texto normal. El bot utiliza **OCR (reconocimiento óptico de caracteres)** para leer el código en pantalla y lo escribe automáticamente con precisión perfecta.

## 🏆 Récord Alcanzado: 261 WPM

El bot ha logrado **261 palabras por minuto (WPM)**, una velocidad **imposible para cualquier humano**

## 📦 Instalación

### Requisitos previos

1. **Python 3.14+**
2. **Tesseract OCR**:
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
   ```

### Instalación del bot

```bash
# 1. Clonar el repositorio
git clone git@github.com:cnexans/wpm-bot.git
cd wpm-bot

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Descargar la base de datos de código (opcional, si esta desactualizado)
curl -o CodeBlocks.json https://raw.githubusercontent.com/silver-dev-org/wpm/main/game/src/data/CodeBlocks.json
```

## 🎮 Uso

### Ejecución básica

```bash
# Usar configuración por defecto (Python, 10ms delay)
python wpm_bot.py

# Especificar velocidad de escritura (en segundos)
python wpm_bot.py 0.01 python

# Cambiar lenguaje
python wpm_bot.py 0.01 javascript
python wpm_bot.py 0.01 golang
```

## 📝 Licencia

Este proyecto es solo para fines educativos y de demostración. No usar para hacer trampa en competencias reales.
