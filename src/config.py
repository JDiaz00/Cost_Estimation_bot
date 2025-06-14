#!/usr/bin/env python3
"""
Configuration settings for the Construction Cost Estimation Chatbot
"""
import os

# Configure OpenAI API key
# Set the environment variable
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Other configuration constants
MAX_HISTORY_LENGTH = 50
DEFAULT_HISTORY_FILE = "chat_history.json"
GRADIO_SERVER_PORT = 7860 