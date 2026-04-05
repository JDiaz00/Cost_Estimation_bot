# Construction Cost Estimation Chatbot

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-green.svg)](https://www.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Chatbot de IA especializado en **cotizacion y estimacion de costos de construccion**. Utiliza agentes reactivos basados en LangGraph y modelos GPT-4 de OpenAI para responder consultas sobre presupuestos, materiales y costos por metro cuadrado.

---

## Caracteristicas

- **Estimacion inteligente de costos** -- respuestas contextuales sobre precios de construccion, materiales y presupuestos
- **Agente reactivo con herramientas** -- arquitectura basada en LangGraph con soporte para herramientas MCP
- **Historial persistente** -- guarda y recupera conversaciones automaticamente en JSON
- **Interfaz web** -- UI interactiva con Gradio accesible desde navegador
- **Interfaz CLI** -- modo linea de comandos para uso rapido
- **Configuracion por entorno** -- variables sensibles gestionadas via `.env`

## Arquitectura

```
Usuario --> run_chatbot.py --> main.py (selector CLI/Web)
                                  |
                    +-------------+-------------+
                    |                           |
               run_cli()                  launch_gradio()
                    |                           |
              ConstructionCostBot         Gradio Blocks UI
                    |
            LangGraph ReAct Agent
                    |
              ChatOpenAI (GPT-4)
                    |
           MCP Tools (opcional)
```

El bot utiliza un agente ReAct (`create_react_agent` de LangGraph) que decide cuando invocar herramientas externas y cuando responder directamente. Si el servidor MCP no esta disponible, se inicializa con herramientas de respaldo.

## Requisitos previos

- **Python 3.10** o superior
- **Clave API de OpenAI** con acceso a GPT-4

## Instalacion

### Con pip

```bash
git clone <url-del-repositorio>
cd Cost_Estimation_bot

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Con Poetry

```bash
git clone <url-del-repositorio>
cd Cost_Estimation_bot

poetry install
poetry shell
```

## Configuracion

Crea un archivo `.env` en la raiz del proyecto:

```env
OPENAI_API_KEY=sk-tu-clave-aqui
MODEL_NAME=gpt-4o                # opcional, por defecto gpt-4o
GRADIO_SERVER_PORT=7860           # opcional, por defecto 7860
```

## Uso

### Ejecutar el chatbot

```bash
python run_chatbot.py
```

Se mostrara un menu para elegir el modo de ejecucion:

1. **Linea de comandos** -- interaccion directa en terminal
2. **Interfaz web (Gradio)** -- abre una UI en `http://localhost:7860`

### Comandos CLI

| Comando   | Descripcion                     |
|-----------|---------------------------------|
| `quit`    | Salir del programa              |
| `history` | Ver historial de conversacion   |
| `clear`   | Limpiar historial               |
| `help`    | Mostrar ayuda                   |

### Ejemplos de consulta

- "Cuanto cuesta construir una casa de 120m2?"
- "Materiales para una losa de 50m2"
- "Presupuesto para pintar 200m2 de pared"

## Estructura del proyecto

```
Cost_Estimation_bot/
├── src/
│   ├── __init__.py              # Paquete principal
│   ├── config.py                # Variables de entorno y constantes
│   ├── construction_bot.py      # Clase ConstructionCostBot (agente ReAct)
│   ├── gradio_interface.py      # Interfaz web con Gradio
│   └── main.py                  # Punto de entrada (selector CLI/Web)
├── run_chatbot.py               # Script ejecutable principal
├── run_gradio_app.py            # Lanzador alternativo para Gradio
├── pyproject.toml               # Configuracion del proyecto (Poetry)
├── requirements.txt             # Dependencias (pip)
├── .env                         # Variables de entorno (no versionado)
└── README.md
```

## Stack tecnologico

| Componente       | Tecnologia                          |
|------------------|-------------------------------------|
| Framework de IA  | LangChain 0.3 + LangGraph          |
| Modelo LLM       | OpenAI GPT-4 via `langchain-openai` |
| Herramientas     | MCP (Model Context Protocol)        |
| Interfaz web     | Gradio 4                            |
| Configuracion    | python-dotenv                       |
| Validacion       | Pydantic 2                          |

## Contribuir

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/mi-feature`)
3. Commit de tus cambios (`git commit -m "Agrega mi feature"`)
4. Push a la rama (`git push origin feature/mi-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto esta bajo la licencia MIT. Ver [LICENSE](LICENSE) para mas detalles.

---

## English Summary

AI-powered chatbot specialized in **construction cost estimation and budgeting**. Built with LangChain, LangGraph (ReAct agents), and OpenAI GPT-4. Features both a CLI and a Gradio web interface with persistent chat history. See the sections above for installation and usage instructions.
