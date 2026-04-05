#!/usr/bin/env python3
"""
Gradio Interface for Construction Cost Estimation Chatbot.

Provides a web-based chat UI for interacting with the construction cost bot.
"""
import asyncio
import logging
from typing import List, Tuple, Optional

import gradio as gr

from .construction_bot import ConstructionCostBot
from .config import GRADIO_SERVER_PORT

logger = logging.getLogger(__name__)

# Module-level bot instance, initialized on first use
_bot: Optional[ConstructionCostBot] = None


async def _get_bot() -> ConstructionCostBot:
    """Return the initialized bot singleton."""
    global _bot
    if _bot is None:
        _bot = ConstructionCostBot()
        await _bot.initialize()
    return _bot


async def chat_interface(
    message: str, history: List[Tuple[str, str]]
) -> Tuple[str, List[Tuple[str, str]]]:
    """Process a chat message and return updated history.

    Args:
        message: User input text.
        history: Current Gradio chat history.

    Returns:
        Tuple of (cleared input, updated history).
    """
    if not message.strip():
        return "", history

    try:
        bot = await _get_bot()
        response = await bot.process_query(message)
        return "", history + [(message, response)]
    except Exception as e:
        logger.error("Error procesando consulta: %s", e, exc_info=True)
        error_response = f"Error procesando la consulta: {str(e)}"
        return "", history + [(message, error_response)]


def clear_chat() -> List:
    """Clear chat history."""
    global _bot
    if _bot:
        _bot.reset_conversation()
    return []


def create_gradio_interface() -> gr.Blocks:
    """Create and configure the Gradio web interface."""
    with gr.Blocks(title="Chatbot de Construcción") as iface:
        gr.Markdown("# Chatbot de Cotización de Construcción")
        gr.Markdown("Especialista en estimación de costos y presupuestos de obras civiles")

        chatbot = gr.Chatbot(label="Chat", height=400)

        with gr.Row():
            msg = gr.Textbox(
                placeholder="Escribe tu consulta sobre construcción aquí...",
                label="Mensaje",
                scale=4,
            )
            submit_btn = gr.Button("Enviar", scale=1)

        clear_btn = gr.Button("Limpiar Chat")

        gr.Markdown(
            """
        ## Tipos de consultas:
        - Costos de construcción
        - Materiales y cantidades
        - Presupuestos de obras
        - Cálculos por m²
        - Cotizaciones de edificación

        ## Ejemplos:
        - "¿Cuánto cuesta construir una casa de 120m²?"
        - "Materiales para una losa de 50m²"
        - "Presupuesto para pintar 200m² de pared"
        """
        )

        def _sync_chat_wrapper(
            message: str, history: List[Tuple[str, str]]
        ) -> Tuple[str, List[Tuple[str, str]]]:
            """Synchronous wrapper around the async chat handler."""
            try:
                return asyncio.run(chat_interface(message, history))
            except RuntimeError:
                # Fallback if an event loop is already running
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, chat_interface(message, history))
                    return future.result()

        submit_btn.click(
            _sync_chat_wrapper,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
        )
        msg.submit(
            _sync_chat_wrapper,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
        )
        clear_btn.click(clear_chat, outputs=[chatbot])

    return iface


async def launch_gradio() -> None:
    """Initialize the bot and launch the Gradio web interface."""
    logger.info("Inicializando chatbot...")
    await _get_bot()
    logger.info("Chatbot inicializado correctamente")

    logger.info("Creando interfaz web...")
    iface = create_gradio_interface()

    logger.info("Lanzando aplicación en puerto %d...", GRADIO_SERVER_PORT)
    try:
        iface.launch(
            server_name="0.0.0.0",
            server_port=GRADIO_SERVER_PORT,
            share=False,
            debug=False,
            show_error=True,
            quiet=False,
        )
    except OSError as e:
        logger.error("Error launching Gradio: %s", e)
        logger.info("Retrying with default configuration...")
        iface.launch()
