# AI Strategic Portfolio Scorecard - Setup Guide

Este proyecto utiliza **Streamlit** para la interfaz y **Ollama (Qwen)** para el motor de inteligencia artificial estratégica local.

---

## 🪟 Guía para Windows

### 1. Instalar Ollama
*   Descarga el instalador desde [ollama.com/download/windows](https://ollama.com/download/windows).
*   Ejecuta el archivo `.exe` y sigue los pasos.
*   Una vez instalado, abre **PowerShell** y ejecuta:
    ```powershell
    ollama run qwen
    ```
    *(Espera a que termine de descargar el modelo de ~4GB).*

### 2. Instalar Python
*   Descarga Python 3.10+ desde [python.org](https://www.python.org/downloads/windows/).
*   **IMPORTANTE**: Durante la instalación, marca la casilla **"Add Python to PATH"**.

### 3. Configurar el Proyecto
Abre una terminal (**PowerShell** o **CMD**) en la carpeta del proyecto:
```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno
.\venv\Scripts\activate

# Instalar librerías
pip install -r requirements.txt
```

### 4. Ejecutar
```powershell
streamlit run version_ia/cartera.py
```

---

## 🍎 Guía para macOS

### 1. Instalar Ollama
*   Descarga el archivo `.zip` desde [ollama.com/download/mac](https://ollama.com/download/mac).
*   Descomprímelo y arrastra **Ollama** a tu carpeta de Aplicaciones.
*   Abre la **Terminal** de Mac y ejecuta:
    ```bash
    ollama run qwen
    ```

### 2. Instalar Python
*   Mac suele traer Python, pero se recomienda instalar la última versión con [Homebrew](https://brew.sh/):
    ```bash
    brew install python
    ```

### 3. Configurar el Proyecto
Abre la **Terminal** en la carpeta del proyecto:
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Instalar librerías
pip install -r requirements.txt
```

### 4. Ejecutar
```bash
streamlit run version_ia/cartera.py
```

---

## 💡 Consejos Comunes
*   **Ollama siempre abierto**: El motor de IA debe estar ejecutándose en segundo plano (busca el icono de la oveja en la barra de tareas o menú superior).
*   **Reset**: Si quieres limpiar la puntuación actual, usa el botón **"🧹 Resetear Puntuación"**.
*   **Escala**: El sistema está optimizado para una escala de **0 a 3** (Nulo a Crítico).
*   **Solución de errores**: Si recibes un "Connection Refused", reinicia la aplicación de Ollama.
