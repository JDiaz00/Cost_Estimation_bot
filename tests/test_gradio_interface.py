"""Tests for src/gradio_interface module."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# chat_interface
# ---------------------------------------------------------------------------

class TestChatInterface:
    @pytest.mark.asyncio
    async def test_empty_message_returns_unchanged_history(self):
        from src.gradio_interface import chat_interface
        result_msg, result_history = await chat_interface("   ", [])
        assert result_msg == ""
        assert result_history == []

    @pytest.mark.asyncio
    async def test_message_processed_successfully(self):
        from src import gradio_interface as gi

        mock_bot = AsyncMock()
        mock_bot.process_query.return_value = "Costo estimado: $10,000"

        with patch.object(gi, "_get_bot", return_value=mock_bot):
            msg, history = await gi.chat_interface("Cuanto cuesta?", [])
        assert msg == ""
        assert len(history) == 1
        assert history[0] == ("Cuanto cuesta?", "Costo estimado: $10,000")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        from src import gradio_interface as gi

        mock_bot = AsyncMock()
        mock_bot.process_query.side_effect = RuntimeError("boom")

        with patch.object(gi, "_get_bot", return_value=mock_bot):
            msg, history = await gi.chat_interface("test", [])
        assert msg == ""
        assert "Error" in history[0][1]

    @pytest.mark.asyncio
    async def test_history_appended(self):
        from src import gradio_interface as gi

        mock_bot = AsyncMock()
        mock_bot.process_query.return_value = "ok"
        existing = [("prev_q", "prev_a")]

        with patch.object(gi, "_get_bot", return_value=mock_bot):
            _, history = await gi.chat_interface("new q", existing)
        assert len(history) == 2


# ---------------------------------------------------------------------------
# clear_chat
# ---------------------------------------------------------------------------

class TestClearChat:
    def test_clear_chat_returns_empty(self):
        from src import gradio_interface as gi
        gi._bot = MagicMock()
        result = gi.clear_chat()
        gi._bot.reset_conversation.assert_called_once()
        assert result == []
        gi._bot = None  # cleanup

    def test_clear_chat_no_bot(self):
        from src import gradio_interface as gi
        gi._bot = None
        result = gi.clear_chat()
        assert result == []


# ---------------------------------------------------------------------------
# create_gradio_interface
# ---------------------------------------------------------------------------

class TestCreateInterface:
    def test_creates_blocks_instance(self):
        from src.gradio_interface import create_gradio_interface
        import gradio as gr
        iface = create_gradio_interface()
        assert isinstance(iface, gr.Blocks)
