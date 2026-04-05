"""
Construction Cost Estimation Chatbot package.

AI-powered chatbot for construction cost estimation and budgeting,
designed for Spanish-speaking users.
"""

from . import config
from .construction_bot import ConstructionCostBot
from .main import main


async def launch_gradio() -> None:
    """Lazy import to avoid loading gradio at package level."""
    from .gradio_interface import launch_gradio as _launch

    await _launch()


__version__ = "1.0.0"
__author__ = "Construction Bot Team"

__all__ = [
    "ConstructionCostBot",
    "launch_gradio",
    "main",
    "config",
]
