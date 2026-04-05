#!/usr/bin/env python3
"""
Construction Cost Estimation Bot.

Main bot class for construction cost queries with message history.
"""
import logging
import os
import json
import asyncio
from datetime import datetime
from typing import List, Any, Dict, Optional

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.tools import tool as langchain_tool

from .config import MAX_HISTORY_LENGTH, DEFAULT_HISTORY_FILE, MODEL_NAME

logger = logging.getLogger(__name__)


class ConstructionCostBot:
    """Chatbot specialized in construction cost estimation and budgeting."""

    def __init__(self, history_file: str = DEFAULT_HISTORY_FILE) -> None:
        self.agent: Optional[Any] = None
        self.tools: List[Any] = []
        self.history_file: str = history_file
        self.message_history: List[Dict[str, str]] = []
        self.max_history_length: int = MAX_HISTORY_LENGTH
        self.last_tools_used: List[Dict[str, Any]] = []
        self.client: Optional[MultiServerMCPClient] = None

    async def initialize(self) -> None:
        """Initialize the agent with tools and load history."""
        llm = ChatOpenAI(model=MODEL_NAME, temperature=0.7)

        self.load_history()

        try:
            await self._initialize_with_mcp_tools(llm)
            logger.info("Initialized with MCP tools")
        except (ConnectionError, RuntimeError, OSError) as e:
            logger.warning("MCP initialization failed: %s", e)
            await self._initialize_with_fallback_tools(llm)
            logger.info("Initialized with fallback tools")

    def load_history(self) -> None:
        """Load chat history from JSON file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.message_history = json.load(f)
                logger.info("Historial cargado: %d mensajes", len(self.message_history))
            else:
                logger.info("Iniciando nuevo historial")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Error cargando historial: %s", e)
            self.message_history = []

    def save_history(self) -> None:
        """Save chat history to JSON file."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.message_history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.warning("Error guardando historial: %s", e)

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        message: Dict[str, str] = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        self.message_history.append(message)

        if len(self.message_history) > self.max_history_length:
            self.message_history = self.message_history[-self.max_history_length :]

        self.save_history()

    def get_recent_history(self, limit: int = 10) -> str:
        """Get recent conversation history formatted as context string."""
        if not self.message_history:
            return ""

        recent_messages = self.message_history[-limit:]
        lines = ["\n--- HISTORIAL DE CONVERSACIÓN RECIENTE ---"]

        for msg in recent_messages:
            timestamp = msg.get("timestamp", "Sin fecha")[:19]
            role_label = "Usuario" if msg["role"] == "user" else "Asistente"
            lines.append(f"[{timestamp}] {role_label}: {msg['content']}")

        lines.append("--- FIN DEL HISTORIAL ---\n")
        return "\n".join(lines)

    def clear_history(self) -> None:
        """Clear all chat history and remove the history file."""
        self.message_history = []
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except OSError as e:
            logger.warning("Error eliminando archivo de historial: %s", e)
        logger.info("Historial limpiado")

    def show_history(self, limit: int = 20) -> None:
        """Display chat history to stdout (CLI use)."""
        if not self.message_history:
            print("No hay mensajes en el historial")
            return

        count = min(limit, len(self.message_history))
        print(f"HISTORIAL DE CONVERSACIÓN (últimos {count} mensajes):")
        print("=" * 60)

        recent_messages = self.message_history[-limit:]
        for i, msg in enumerate(recent_messages, 1):
            timestamp = msg.get("timestamp", "Sin fecha")[:19]
            role = msg["role"].upper()
            preview = msg["content"][:100]
            ellipsis = "..." if len(msg["content"]) > 100 else ""
            print(f"{i}. [{timestamp}] {role}:")
            print(f"   {preview}{ellipsis}")
            print()

    async def _initialize_with_mcp_tools(self, llm: ChatOpenAI) -> None:
        """Initialize the agent using MCP server tools."""
        self.client = MultiServerMCPClient(
            {
                "math": {
                    "transport": "streamable_http",
                    "url": "http://localhost:8000/mcp",
                },
            }
        )

        self.tools = await self.client.get_tools()

        logger.info("MCP tools found: %d", len(self.tools))
        for i, t in enumerate(self.tools):
            name = getattr(t, "name", "Unknown")
            logger.debug("  Tool %d: %s", i + 1, name)

        if not self.tools:
            raise RuntimeError("No tools loaded from MCP server")

        self.agent = create_react_agent(model=llm, tools=self.tools)
        logger.info("React agent created with %d MCP tools", len(self.tools))

    async def _initialize_with_fallback_tools(self, llm: ChatOpenAI) -> None:
        """Initialize the agent with built-in fallback tools when MCP is unavailable."""

        @langchain_tool
        def construction_query(query: str) -> str:
            """Responde preguntas sobre construcción y cotizaciones."""
            return f"Información sobre construcción para: {query}"

        self.tools = [construction_query]
        self.agent = create_react_agent(model=llm, tools=self.tools)

    def get_system_prompt(self) -> str:
        """Return the system prompt for the construction cost estimation agent."""
        return """Eres un experto en cotización y estimación de costos de construcción.

INSTRUCCIONES IMPORTANTES:
- SOLO utiliza la herramienta construction_query para preguntas relacionadas con CONSTRUCCIÓN
- Antes de usar cualquier herramienta, EVALÚA si la pregunta es sobre construcción
- Preguntas de construcción incluyen: costos, materiales, edificación, obras civiles, presupuestos de construcción
- Si la pregunta NO es sobre construcción, responde directamente sin usar herramientas
- Considera el historial de conversación para dar respuestas más contextuales

TEMAS DE CONSTRUCCIÓN:
- Costos de construcción
- Materiales de construcción
- Presupuestos de obras
- Cotizaciones de edificación
- Cantidades de materiales
- Precios por m²

TEMAS NO CONSTRUCCIÓN:
- Preguntas generales
- Otros temas no relacionados
- Conversación casual

Cuando uses la herramienta construction_query, proporciona estimaciones claras con números específicos y desglose detallado."""

    async def ask(self, question: str) -> str:
        """Process a construction cost question with history context.

        Args:
            question: The user's question text.

        Returns:
            The assistant's response string.
        """
        if not self.agent:
            return "Error: Bot no inicializado"

        self.add_to_history("user", question)
        logger.debug("Pregunta recibida: %s", question)

        try:
            history_context = self.get_recent_history(5)
            full_prompt = (
                f"{self.get_system_prompt()}\n\n"
                f"{history_context}"
                f"Pregunta actual del usuario: {question}"
            )

            logger.debug(
                "Prompt length: %d chars, tools: %d, history: %s",
                len(full_prompt),
                len(self.tools),
                bool(history_context.strip()),
            )

            result = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=full_prompt)]}
            )

            # Extract response and track tools used
            response = ""
            tools_used: List[Dict[str, Any]] = []

            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                for msg in messages:
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            tool_name = getattr(tool_call, "name", "Unknown")
                            tools_used.append(
                                {
                                    "name": tool_name,
                                    "type": "mcp_tool" if hasattr(tool_call, "args") else "fallback_tool",
                                    "args": getattr(tool_call, "args", {}),
                                    "used_at": datetime.now().isoformat(),
                                }
                            )

                if messages and hasattr(messages[-1], "content"):
                    response = messages[-1].content

            if not response:
                response = str(result)

            # Add response to history with tools info
            response_with_tools = response
            if tools_used:
                tool_names = ", ".join(t["name"] for t in tools_used)
                response_with_tools += f"\n\nHerramientas utilizadas: {tool_names}"

            self.add_to_history("assistant", response_with_tools)
            self.last_tools_used = tools_used

            return response

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error("Error procesando consulta: %s", e, exc_info=True)
            self.add_to_history("assistant", error_msg)
            self.last_tools_used = []
            return error_msg

    async def process_query(self, query: str) -> str:
        """Process query (compatibility wrapper for Gradio integration)."""
        return await self.ask(query)

    def get_last_tools_used(self) -> List[Dict[str, Any]]:
        """Get tools used in the last query."""
        return self.last_tools_used

    def reset_conversation(self) -> None:
        """Reset conversation and clear tools tracking."""
        self.clear_history()
        self.last_tools_used = []

    def get_chat_history_for_gradio(self) -> List[tuple[str, str]]:
        """Get chat history formatted for Gradio chatbot component."""
        chat_history: List[tuple[str, str]] = []
        temp_user_msg: Optional[str] = None

        for msg in self.message_history:
            if msg["role"] == "user":
                temp_user_msg = msg["content"]
            elif msg["role"] == "assistant" and temp_user_msg:
                assistant_content = msg["content"]
                if "\n\nHerramientas utilizadas:" in assistant_content:
                    assistant_content = assistant_content.split("\n\nHerramientas utilizadas:")[0]
                chat_history.append((temp_user_msg, assistant_content))
                temp_user_msg = None

        return chat_history
