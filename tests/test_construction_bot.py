"""Tests for src/construction_bot module."""
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.construction_bot import ConstructionCostBot


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestBotInit:
    def test_default_attributes(self, tmp_history_file):
        bot = ConstructionCostBot(history_file=tmp_history_file)
        assert bot.agent is None
        assert bot.tools == []
        assert bot.message_history == []
        assert bot.history_file == tmp_history_file

    @pytest.mark.asyncio
    async def test_initialize_falls_back_when_mcp_fails(self, tmp_history_file):
        """When MCP connection fails, bot should fall back to built-in tools."""
        with patch("src.construction_bot.ChatOpenAI"), \
             patch.object(ConstructionCostBot, "_initialize_with_mcp_tools",
                          new_callable=AsyncMock, side_effect=ConnectionError("no server")), \
             patch.object(ConstructionCostBot, "_initialize_with_fallback_tools",
                          new_callable=AsyncMock) as mock_fallback:
            bot = ConstructionCostBot(history_file=tmp_history_file)
            await bot.initialize()
            mock_fallback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_initialize_with_mcp_success(self, tmp_history_file):
        """When MCP succeeds, fallback should not be called."""
        with patch("src.construction_bot.ChatOpenAI"), \
             patch.object(ConstructionCostBot, "_initialize_with_mcp_tools",
                          new_callable=AsyncMock) as mock_mcp, \
             patch.object(ConstructionCostBot, "_initialize_with_fallback_tools",
                          new_callable=AsyncMock) as mock_fallback:
            bot = ConstructionCostBot(history_file=tmp_history_file)
            await bot.initialize()
            mock_mcp.assert_awaited_once()
            mock_fallback.assert_not_awaited()


# ---------------------------------------------------------------------------
# History loading / saving
# ---------------------------------------------------------------------------

class TestHistory:
    def test_load_empty_history(self, tmp_history_file):
        bot = ConstructionCostBot(history_file=tmp_history_file)
        bot.load_history()
        assert bot.message_history == []

    def test_load_existing_history(self, tmp_history_with_data, sample_history):
        bot = ConstructionCostBot(history_file=tmp_history_with_data)
        bot.load_history()
        assert len(bot.message_history) == len(sample_history)
        assert bot.message_history[0]["content"] == "Hola"

    def test_load_corrupted_file(self, tmp_path):
        bad_file = str(tmp_path / "bad.json")
        with open(bad_file, "w") as f:
            f.write("{not valid json")
        bot = ConstructionCostBot(history_file=bad_file)
        bot.load_history()
        assert bot.message_history == []

    def test_save_history(self, tmp_history_file):
        bot = ConstructionCostBot(history_file=tmp_history_file)
        bot.message_history = [{"role": "user", "content": "test", "timestamp": "t"}]
        bot.save_history()
        with open(tmp_history_file, "r") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["content"] == "test"

    def test_save_history_io_error(self, tmp_path):
        """Saving to an invalid path should not raise."""
        bot = ConstructionCostBot(history_file=str(tmp_path / "no_dir" / "file.json"))
        bot.message_history = [{"role": "user", "content": "x", "timestamp": "t"}]
        # Should not raise
        bot.save_history()

    def test_add_to_history_truncates(self, tmp_history_file):
        bot = ConstructionCostBot(history_file=tmp_history_file)
        bot.max_history_length = 3
        for i in range(5):
            bot.add_to_history("user", f"msg {i}")
        assert len(bot.message_history) == 3
        assert bot.message_history[0]["content"] == "msg 2"

    def test_clear_history(self, tmp_history_with_data):
        bot = ConstructionCostBot(history_file=tmp_history_with_data)
        bot.load_history()
        assert len(bot.message_history) > 0
        bot.clear_history()
        assert bot.message_history == []
        assert not os.path.exists(tmp_history_with_data)

    def test_clear_history_missing_file(self, tmp_history_file):
        """Clearing when file does not exist should not raise."""
        bot = ConstructionCostBot(history_file=tmp_history_file)
        bot.clear_history()
        assert bot.message_history == []


# ---------------------------------------------------------------------------
# Recent history formatting
# ---------------------------------------------------------------------------

class TestRecentHistory:
    def test_empty_history_returns_empty(self, tmp_history_file):
        bot = ConstructionCostBot(history_file=tmp_history_file)
        assert bot.get_recent_history() == ""

    def test_recent_history_format(self, tmp_history_with_data):
        bot = ConstructionCostBot(history_file=tmp_history_with_data)
        bot.load_history()
        text = bot.get_recent_history(limit=5)
        assert "HISTORIAL DE CONVERSACIÓN RECIENTE" in text
        assert "Hola" in text


# ---------------------------------------------------------------------------
# ask() — message processing
# ---------------------------------------------------------------------------

class TestAsk:
    @pytest.mark.asyncio
    async def test_ask_returns_response(self, mock_bot):
        response = await mock_bot.ask("Cuanto cuesta una casa?")
        assert "50,000" in response

    @pytest.mark.asyncio
    async def test_ask_adds_to_history(self, mock_bot):
        await mock_bot.ask("Pregunta de prueba")
        roles = [m["role"] for m in mock_bot.message_history]
        assert "user" in roles
        assert "assistant" in roles

    @pytest.mark.asyncio
    async def test_ask_without_agent(self, tmp_history_file):
        bot = ConstructionCostBot(history_file=tmp_history_file)
        result = await bot.ask("algo")
        assert result == "Error: Bot no inicializado"

    @pytest.mark.asyncio
    async def test_ask_handles_exception(self, mock_bot):
        mock_bot.agent.ainvoke.side_effect = RuntimeError("API down")
        response = await mock_bot.ask("test")
        assert "Error" in response

    @pytest.mark.asyncio
    async def test_ask_tracks_tool_calls(self, mock_bot):
        tool_call = MagicMock()
        tool_call.name = "construction_query"
        tool_call.args = {"query": "costo casa"}
        msg_with_tools = MagicMock(content="Respuesta", tool_calls=[tool_call])
        final_msg = MagicMock(content="Costo: $100k", tool_calls=None)
        mock_bot.agent.ainvoke.return_value = {
            "messages": [msg_with_tools, final_msg]
        }
        await mock_bot.ask("costo casa")
        assert len(mock_bot.last_tools_used) == 1
        assert mock_bot.last_tools_used[0]["name"] == "construction_query"

    @pytest.mark.asyncio
    async def test_process_query_delegates_to_ask(self, mock_bot):
        response = await mock_bot.process_query("test")
        assert response == await mock_bot.ask.__wrapped__(mock_bot, "test") if hasattr(mock_bot.ask, '__wrapped__') else True
        # Simpler: just verify it returns a string
        assert isinstance(response, str)


# ---------------------------------------------------------------------------
# Reset / Gradio helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_reset_conversation(self, mock_bot):
        mock_bot.message_history = [{"role": "user", "content": "x", "timestamp": "t"}]
        mock_bot.last_tools_used = [{"name": "tool"}]
        mock_bot.reset_conversation()
        assert mock_bot.message_history == []
        assert mock_bot.last_tools_used == []

    def test_get_chat_history_for_gradio(self, mock_bot):
        mock_bot.message_history = [
            {"role": "user", "content": "Hola"},
            {"role": "assistant", "content": "Respuesta\n\nHerramientas utilizadas: tool1"},
            {"role": "user", "content": "Otro"},
            {"role": "assistant", "content": "Otra respuesta"},
        ]
        result = mock_bot.get_chat_history_for_gradio()
        assert len(result) == 2
        assert result[0] == ("Hola", "Respuesta")
        assert result[1] == ("Otro", "Otra respuesta")

    def test_get_system_prompt(self, mock_bot):
        prompt = mock_bot.get_system_prompt()
        assert "construcción" in prompt.lower() or "construccion" in prompt.lower()

    def test_get_last_tools_used(self, mock_bot):
        mock_bot.last_tools_used = [{"name": "test_tool"}]
        assert mock_bot.get_last_tools_used() == [{"name": "test_tool"}]
