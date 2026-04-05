#!/usr/bin/env python3
"""
Configuration settings for the Construction Cost Estimation Chatbot.

Loads environment variables from .env and provides project-wide constants.
"""
import os
import logging

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "gpt-4o")

if not OPENAI_API_KEY:
    logger.warning(
        "OPENAI_API_KEY no está configurada. "
        "Crea un archivo .env con tu clave o expórtala como variable de entorno."
    )

# Other configuration constants
MAX_HISTORY_LENGTH: int = 50
DEFAULT_HISTORY_FILE: str = "chat_history.json"
GRADIO_SERVER_PORT: int = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
