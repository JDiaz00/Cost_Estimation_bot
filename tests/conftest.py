"""Shared fixtures for the Construction Cost Estimation Bot test suite."""
import os
import sys
import json
import types
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Set dummy API key before any source imports
# ---------------------------------------------------------------------------
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy-key-for-testing")

# ---------------------------------------------------------------------------
# Ensure langchain compatibility shims exist so the source code can import
# from langchain.schema and langchain.tools regardless of installed version.
# ---------------------------------------------------------------------------
try:
    from langchain.schema import HumanMessage  # noqa: F401
except (ImportError, ModuleNotFoundError):
    # langchain v1.x dropped langchain.schema — alias from langchain_core
    from langchain_core import messages as _msgs

    _schema_mod = types.ModuleType("langchain.schema")
    _schema_mod.HumanMessage = _msgs.HumanMessage  # type: ignore[attr-defined]
    _schema_mod.AIMessage = _msgs.AIMessage  # type: ignore[attr-defined]
    sys.modules["langchain.schema"] = _schema_mod

try:
    from langchain.tools import tool  # noqa: F401
except (ImportError, ModuleNotFoundError):
    from langchain_core import tools as _tools_mod

    _lt_mod = types.ModuleType("langchain.tools")
    _lt_mod.tool = _tools_mod.tool  # type: ignore[attr-defined]
    sys.modules["langchain.tools"] = _lt_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _set_dummy_api_key(monkeypatch):
    """Ensure OPENAI_API_KEY is always set during tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-testing")


@pytest.fixture
def tmp_history_file(tmp_path):
    """Return a temporary file path for chat history."""
    return str(tmp_path / "test_history.json")


@pytest.fixture
def sample_history():
    """Sample chat history data."""
    return [
        {"role": "user", "content": "Hola", "timestamp": "2026-01-01T00:00:00"},
        {"role": "assistant", "content": "Hola, soy el bot de construccion", "timestamp": "2026-01-01T00:00:01"},
    ]


@pytest.fixture
def tmp_history_with_data(tmp_path, sample_history):
    """Create a temporary history file pre-populated with sample data."""
    path = str(tmp_path / "test_history.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample_history, f)
    return path


@pytest.fixture
def mock_agent():
    """A mock LangGraph agent that returns a canned response."""
    agent = AsyncMock()
    agent.ainvoke.return_value = {
        "messages": [
            MagicMock(content="El costo estimado es $50,000 USD", tool_calls=None),
        ]
    }
    return agent


@pytest.fixture
def mock_bot(tmp_history_file, mock_agent):
    """A ConstructionCostBot with mocked agent, ready to use."""
    from src.construction_bot import ConstructionCostBot

    bot = ConstructionCostBot(history_file=tmp_history_file)
    bot.agent = mock_agent
    bot.tools = [MagicMock(name="construction_query")]
    return bot
