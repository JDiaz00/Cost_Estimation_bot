"""Tests for src/config module."""
import os
import importlib


def test_openai_api_key_loaded(monkeypatch):
    """Config should pick up OPENAI_API_KEY from the environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
    import src.config as cfg
    importlib.reload(cfg)
    assert cfg.OPENAI_API_KEY == "sk-test-123"


def test_default_model_name(monkeypatch):
    """MODEL_NAME defaults to gpt-4o when not set."""
    monkeypatch.delenv("MODEL_NAME", raising=False)
    import src.config as cfg
    importlib.reload(cfg)
    assert cfg.MODEL_NAME == "gpt-4o"


def test_custom_model_name(monkeypatch):
    """MODEL_NAME should reflect the environment variable."""
    monkeypatch.setenv("MODEL_NAME", "gpt-3.5-turbo")
    import src.config as cfg
    importlib.reload(cfg)
    assert cfg.MODEL_NAME == "gpt-3.5-turbo"


def test_default_constants(monkeypatch):
    """Verify hard-coded defaults for history length, file, and port."""
    monkeypatch.delenv("GRADIO_SERVER_PORT", raising=False)
    import src.config as cfg
    importlib.reload(cfg)
    assert cfg.MAX_HISTORY_LENGTH == 50
    assert cfg.DEFAULT_HISTORY_FILE == "chat_history.json"
    assert cfg.GRADIO_SERVER_PORT == 7860


def test_custom_gradio_port(monkeypatch):
    """GRADIO_SERVER_PORT should be read from the environment."""
    monkeypatch.setenv("GRADIO_SERVER_PORT", "9999")
    import src.config as cfg
    importlib.reload(cfg)
    assert cfg.GRADIO_SERVER_PORT == 9999


def test_missing_api_key_does_not_crash(monkeypatch):
    """Config should load without error even if OPENAI_API_KEY is missing."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import src.config as cfg
    importlib.reload(cfg)
    assert cfg.OPENAI_API_KEY == ""
