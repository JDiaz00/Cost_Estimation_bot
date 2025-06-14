#!/usr/bin/env python3
"""
Construction Cost Estimation Bot
Main bot class for construction cost queries with message history
"""
import os
import json
import asyncio
from datetime import datetime
from typing import List, Any, Dict
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from .config import MAX_HISTORY_LENGTH, DEFAULT_HISTORY_FILE

class ConstructionCostBot:
    def __init__(self, history_file: str = DEFAULT_HISTORY_FILE):
        self.agent = None
        self.tools = []
        self.history_file = history_file
        self.message_history: List[Dict] = []
        self.max_history_length = MAX_HISTORY_LENGTH
        self.last_tools_used = []  # Para rastrear herramientas usadas en la última consulta
        
    async def initialize(self):
        """Initialize the agent with tools and load history"""
        llm = ChatOpenAI(model="gpt-4.1-2025-04-14", temperature=0.7)
        
        # Load existing history
        self.load_history()
        
        try:
            await self._initialize_with_mcp_tools(llm)
            print("✅ Initialized with MCP tools")
        except Exception as e:
            print(f"⚠️ MCP failed: {e}")
            await self._initialize_with_fallback_tools(llm)
            print("✅ Initialized with fallback tools")
    
    def load_history(self):
        """Load chat history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.message_history = json.load(f)
                print(f"📚 Historial cargado: {len(self.message_history)} mensajes")
            else:
                print("📚 Iniciando nuevo historial")
        except Exception as e:
            print(f"⚠️ Error cargando historial: {e}")
            self.message_history = []
    
    def save_history(self):
        """Save chat history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.message_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error guardando historial: {e}")
    
    def add_to_history(self, role: str, content: str):
        """Add message to history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.message_history.append(message)
        
        # Limit history length
        if len(self.message_history) > self.max_history_length:
            self.message_history = self.message_history[-self.max_history_length:]
        
        # Save to file
        self.save_history()
    
    def get_recent_history(self, limit: int = 10):
        """Get recent conversation history as context"""
        if not self.message_history:
            return ""
        
        recent_messages = self.message_history[-limit:]
        history_text = "\n--- HISTORIAL DE CONVERSACIÓN RECIENTE ---\n"
        
        for msg in recent_messages:
            timestamp = msg.get('timestamp', 'Sin fecha')[:19]  # Solo fecha y hora
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            history_text += f"{role_emoji} [{timestamp}] {msg['role']}: {msg['content']}\n"
        
        history_text += "--- FIN DEL HISTORIAL ---\n\n"
        return history_text
    
    def clear_history(self):
        """Clear chat history"""
        self.message_history = []
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except Exception as e:
            print(f"⚠️ Error eliminando archivo de historial: {e}")
        print("🗑️ Historial limpiado")
    
    def show_history(self, limit: int = 20):
        """Display chat history"""
        if not self.message_history:
            print("📚 No hay mensajes en el historial")
            return
        
        print(f"📚 HISTORIAL DE CONVERSACIÓN (últimos {min(limit, len(self.message_history))} mensajes):")
        print("=" * 60)
        
        recent_messages = self.message_history[-limit:]
        for i, msg in enumerate(recent_messages, 1):
            timestamp = msg.get('timestamp', 'Sin fecha')[:19]
            role = msg['role'].upper()
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            
            print(f"{i}. {role_emoji} [{timestamp}] {role}:")
            print(f"   {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
            print()

    async def _initialize_with_mcp_tools(self, llm):
        """Initialize with MCP tools"""
        self.client = MultiServerMCPClient({
            "math": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp"
            },
        })
        
        self.tools = await self.client.get_tools()
        
        # Print detailed information about MCP tools
        print(f"🔧 TOOLS EXTRACTED FROM MCP SERVER:")
        print(f"   Total tools found: {len(self.tools)}")
        
        for i, tool in enumerate(self.tools):
            print(f"   Tool {i+1}: {tool.name if hasattr(tool, 'name') else 'Unknown'}")
            print(f"   Description: {tool.description if hasattr(tool, 'description') else 'No description'}")
            print(f"   Tool type: {type(tool)}")
            if hasattr(tool, 'input_schema'):
                print(f"   Input schema: {tool.input_schema}")
            print()
        
        if not self.tools:
            raise RuntimeError("No tools loaded from MCP server")
        
        self.agent = create_react_agent(model=llm, tools=self.tools)
        print(f"✅ React agent created successfully with {len(self.tools)} MCP tools")
        
        self.agent = create_react_agent(model=llm, tools=self.tools)
    
    async def _initialize_with_fallback_tools(self, llm):
        """Initialize with fallback tools when MCP is not available"""
        from langchain.tools import tool
        
        @tool
        def construction_query(query: str):
            """Responde preguntas sobre construcción y cotizaciones"""
            return f"Información sobre construcción para: {query}"
        
        self.tools = [construction_query]
        self.agent = create_react_agent(model=llm, tools=self.tools)
    
    def get_system_prompt(self):
        return """Eres un experto en cotización y estimación de costos de construcción.

INSTRUCCIONES IMPORTANTES:
- SOLO utiliza la herramienta construction_query para preguntas relacionadas con CONSTRUCCIÓN
- Antes de usar cualquier herramienta, EVALÚA si la pregunta es sobre construcción
- Preguntas de construcción incluyen: costos, materiales, edificación, obras civiles, presupuestos de construcción
- Si la pregunta NO es sobre construcción, responde directamente sin usar herramientas
- Considera el historial de conversación para dar respuestas más contextuales

TEMAS DE CONSTRUCCIÓN:
✅ Costos de construcción
✅ Materiales de construcción  
✅ Presupuestos de obras
✅ Cotizaciones de edificación
✅ Cantidades de materiales
✅ Precios por m²

TEMAS NO CONSTRUCCIÓN:
❌ Preguntas generales
❌ Otros temas no relacionados
❌ Conversación casual

Cuando uses la herramienta construction_query, proporciona estimaciones claras con números específicos y desglose detallado."""

    async def ask(self, question: str):
        """Process a construction cost question with history context"""
        if not self.agent:
            return "❌ Error: Bot no inicializado"
        
        # Add question to history
        self.add_to_history("user", question)
        
        print(f"📤 PREGUNTA ENVIADA AL AGENT:")
        print(f"   Pregunta original: {question}")
        print()
        
        try:
            # Get recent history for context
            history_context = self.get_recent_history(5)  # Últimos 5 intercambios
            
            # Create message with system context and history
            full_prompt = f"{self.get_system_prompt()}\n\n{history_context}Pregunta actual del usuario: {question}"
            
            print(f"🔄 PROMPT COMPLETO ENVIADO:")
            print(f"   Longitud del prompt: {len(full_prompt)} caracteres")
            print(f"   Herramientas disponibles: {len(self.tools)}")
            print(f"   Contexto de historial incluido: {'Sí' if history_context.strip() else 'No'}")
            print()
            
            # Use agent to process question
            result = await self.agent.ainvoke({"messages": [HumanMessage(content=full_prompt)]})
            
            print(f"📊 RESULTADO COMPLETO DEL AGENT:")
            print(f"   Tipo de resultado: {type(result)}")
            print(f"   Claves del resultado: {list(result.keys()) if isinstance(result, dict) else 'No es dict'}")
            print()
            
            # Extract response and track tools used
            response = ""
            tools_used = []
            if isinstance(result, dict) and "messages" in result:
                messages = result["messages"]
                print(f"📨 MENSAJES EN EL RESULTADO:")
                print(f"   Total de mensajes: {len(messages)}")
                
                for i, msg in enumerate(messages):
                    print(f"   Mensaje {i+1}:")
                    print(f"     Tipo: {type(msg).__name__}")
                    print(f"     Contenido: {getattr(msg, 'content', str(msg))[:200]}...")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print(f"     Tool calls: {len(msg.tool_calls)} llamadas")
                        for j, tool_call in enumerate(msg.tool_calls):
                            tool_name = getattr(tool_call, 'name', 'Unknown')
                            print(f"       Tool {j+1}: {tool_name}")
                            tools_used.append({
                                "name": tool_name,
                                "type": "mcp_tool" if hasattr(tool_call, 'args') else "fallback_tool",
                                "args": getattr(tool_call, 'args', {}),
                                "used_at": datetime.now().isoformat()
                            })
                    print()
                
                if messages and hasattr(messages[-1], 'content'):
                    response = messages[-1].content
                    print(f"✅ RESPUESTA FINAL EXTRAÍDA:")
                    print(f"   Longitud: {len(response)} caracteres")
                    print(f"   Contenido: {response}")
                    print()
            
            if not response:
                response = str(result)
                print(f"🔄 CONVERSIÓN A STRING (FALLBACK):")
                print(f"   Resultado: {response[:500]}...")
                print()
            
            # Add response to history with tools info
            response_with_tools = response
            if tools_used:
                tools_info = f"\n\n🔧 Herramientas utilizadas: {', '.join([tool['name'] for tool in tools_used])}"
                response_with_tools += tools_info
            
            self.add_to_history("assistant", response_with_tools)
            
            # Store tools used in a separate attribute for external access
            self.last_tools_used = tools_used
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            print(f"💥 ERROR EN PROCESAMIENTO:")
            print(f"   Tipo de error: {type(e).__name__}")
            print(f"   Mensaje de error: {str(e)}")
            print()
            
            # Add error to history
            self.add_to_history("assistant", error_msg)
            
            # Clear tools used on error
            self.last_tools_used = []
            
            return error_msg

    async def process_query(self, query: str):
        """Process query - compatibility method for Gradio integration"""
        return await self.ask(query)
    
    def get_last_tools_used(self):
        """Get tools used in the last query"""
        return getattr(self, 'last_tools_used', [])
    
    def reset_conversation(self):
        """Reset conversation and clear tools tracking"""
        self.clear_history()
        self.last_tools_used = []

    def get_chat_history_for_gradio(self):
        """Get chat history formatted for Gradio chatbot component"""
        chat_history = []
        temp_user_msg = None
        
        for msg in self.message_history:
            if msg['role'] == 'user':
                temp_user_msg = msg['content']
            elif msg['role'] == 'assistant' and temp_user_msg:
                # Clean up assistant response (remove tools info for display)
                assistant_content = msg['content']
                if "\n\n🔧 Herramientas utilizadas:" in assistant_content:
                    assistant_content = assistant_content.split("\n\n🔧 Herramientas utilizadas:")[0]
                
                chat_history.append((temp_user_msg, assistant_content))
                temp_user_msg = None
        
        return chat_history 