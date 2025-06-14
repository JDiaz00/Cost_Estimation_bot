# 🏗️ Construction Cost Estimation Chatbot

Un chatbot inteligente especializado en cotización y estimación de costos de construcción, con interfaz web y línea de comandos.

## 📁 Estructura del Proyecto

```
AGENTE-RAG/
├── src/
│   ├── __init__.py           # Paquete principal
│   ├── config.py             # Configuraciones y constantes
│   ├── construction_bot.py   # Clase principal del chatbot
│   ├── gradio_interface.py   # Interfaz web con Gradio
│   └── main.py              # Punto de entrada principal
├── run_chatbot.py           # Script ejecutable
├── requirements.txt         # Dependencias
└── README.md               # Documentación
```

## 🚀 Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd AGENTE-RAG
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar API Key**:
   - Edita `src/config.py` con tu API key de OpenAI

## 💻 Uso

### Ejecutar el chatbot:
```bash
python run_chatbot.py
```

### Opciones disponibles:
- **1**: Interfaz de línea de comandos
- **2**: Interfaz web (Gradio)

## 🌟 Características

- **🤖 IA Especializada**: Entrenada específicamente para construcción
- **💾 Historial Persistente**: Guarda conversaciones automáticamente
- **🌐 Interfaz Web**: UI moderna con Gradio
- **📱 Responsive**: Funciona en desktop y móvil
- **🔧 Herramientas MCP**: Integración con herramientas externas

## 📊 Tipos de Consultas

- 💰 Costos de construcción
- 🧱 Materiales y cantidades
- 📊 Presupuestos de obras
- 📐 Cálculos por m²
- 🏠 Cotizaciones de edificación

## 🛠️ Módulos

### `src/config.py`
Configuraciones del sistema, API keys y constantes.

### `src/construction_bot.py`
Clase principal `ConstructionCostBot` que maneja:
- Inicialización del agente de IA
- Gestión de historial de conversación
- Procesamiento de consultas
- Integración con herramientas MCP

### `src/gradio_interface.py`
Interfaz web con Gradio que incluye:
- Chat interactivo
- Limpieza de historial
- Interfaz responsive

### `src/main.py`
Punto de entrada que permite elegir entre:
- Interfaz de línea de comandos
- Interfaz web

## 📝 Comandos CLI

- `quit` - Salir del programa
- `history` - Ver historial de conversación
- `clear` - Limpiar historial
- `help` - Mostrar ayuda

## 🔧 Desarrollo

Para desarrollar o modificar el chatbot:

1. **Estructura modular**: Cada funcionalidad en su propio archivo
2. **Importaciones relativas**: Usar `from .module import function`
3. **Configuración centralizada**: Todas las constantes en `config.py`
4. **Async/await**: Soporte completo para operaciones asíncronas

## 📋 Dependencias Principales

- **LangChain**: Framework de IA conversacional
- **OpenAI**: Modelo GPT-4 para procesamiento
- **Gradio**: Interfaz web interactiva
- **LangGraph**: Agentes reactivos
- **AsyncIO**: Programación asíncrona

## 🐛 Troubleshooting

### Error de importaciones:
```bash
# Asegurarse de ejecutar desde el directorio raíz
python run_chatbot.py
```

### Error de API Key:
```python
# Verificar en src/config.py que la API key sea válida
OPENAI_API_KEY = "tu-api-key-aquí"
```

## 📞 Soporte

Para problemas o sugerencias, crear un issue en el repositorio del proyecto. 