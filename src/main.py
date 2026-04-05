#!/usr/bin/env python3
"""
Main entry point for Construction Cost Estimation Chatbot.

Provides CLI and web interface launch options.
"""

import asyncio
import logging

from .construction_bot import ConstructionCostBot

logger = logging.getLogger(__name__)


async def run_cli() -> None:
    """Run the interactive command-line interface."""
    bot = ConstructionCostBot()
    await bot.initialize()

    print("Chatbot de Cotización de Construcción con Historial")
    print("=" * 50)
    print("Comandos especiales:")
    print("  'quit'    - Salir del programa")
    print("  'history' - Ver historial de conversación")
    print("  'clear'   - Limpiar historial")
    print("  'help'    - Mostrar esta ayuda")
    print()

    while True:
        try:
            question = input("Pregunta: ").strip()

            if question.lower() == "quit":
                break
            elif question.lower() == "history":
                bot.show_history()
                continue
            elif question.lower() == "clear":
                bot.clear_history()
                continue
            elif question.lower() == "help":
                print("Comandos disponibles:")
                print("  'quit'    - Salir del programa")
                print("  'history' - Ver historial de conversación")
                print("  'clear'   - Limpiar historial")
                print("  'help'    - Mostrar esta ayuda")
                print("  Cualquier otra cosa - Hacer una pregunta sobre construcción")
                continue
            elif not question:
                continue

            print("Procesando...")
            response = await bot.ask(question)
            print(f"Respuesta: {response}")
            print()

        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            logger.error("Error inesperado: %s", e, exc_info=True)
            print(f"Error: {e}")


async def main() -> None:
    """Main function — prompts user to choose CLI or web interface."""
    choice = input(
        "¿Cómo quieres ejecutar el chatbot?\n"
        "1. Línea de comandos\n"
        "2. Interfaz web (Gradio)\n"
        "Elige (1/2): "
    ).strip()

    if choice == "2":
        from .gradio_interface import launch_gradio

        await launch_gradio()
    else:
        await run_cli()


if __name__ == "__main__":
    asyncio.run(main())
