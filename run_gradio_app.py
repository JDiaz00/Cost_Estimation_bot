#!/usr/bin/env python3
"""Launcher script for the Construction Cost Estimation Gradio App."""
import sys
import os
import logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_dependencies() -> bool:
    """Check if required Python packages are installed."""
    required_packages = [
        "gradio",
        "langchain",
        "langchain_openai",
        "langchain_mcp_adapters",
        "langgraph",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        logger.error("Paquetes faltantes:")
        for pkg in missing_packages:
            logger.error("   - %s", pkg)
        logger.info("Para instalar: pip install -r requirements.txt")
        return False

    return True


def main() -> int:
    """Launch the Gradio web application."""
    print("Iniciando Chatbot de Construcción con Gradio")
    print("-" * 50)

    # Load environment variables
    load_dotenv()

    # Check dependencies
    print("Verificando dependencias...")
    if not check_dependencies():
        return 1
    print("Todas las dependencias están instaladas")

    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning(
            "OPENAI_API_KEY no encontrada. "
            "Crea un archivo .env con tu clave API."
        )

    print()
    print("Iniciando servidor Gradio...")
    print("La aplicación estará disponible en: http://localhost:7860")
    print("Presiona Ctrl+C para detener la aplicación")
    print("-" * 50)

    try:
        import asyncio
        from src.gradio_interface import launch_gradio

        asyncio.run(launch_gradio())
    except KeyboardInterrupt:
        print("\nAplicación detenida por el usuario")
        return 0
    except Exception as e:
        logger.error("Error ejecutando la aplicación: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
