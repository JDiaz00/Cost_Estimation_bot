#!/usr/bin/env python3
"""
Gradio Interface for Construction Cost Estimation Chatbot
Web UI implementation
"""
import asyncio
import gradio as gr
from .construction_bot import ConstructionCostBot
from .config import GRADIO_SERVER_PORT

# Global bot instance
bot = None

async def initialize_bot():
    """Initialize the global bot instance"""
    global bot
    if bot is None:
        bot = ConstructionCostBot()
        await bot.initialize()
    return bot

async def chat_interface(message, history):
    """Gradio chat interface function"""
    global bot
    if bot is None:
        bot = await initialize_bot()
    
    if not message.strip():
        return "", history
    
    try:
        # Process the message
        response = await bot.process_query(message)
        
        # Update history
        updated_history = history + [(message, response)]
        
        return "", updated_history
        
    except Exception as e:
        error_response = f"❌ Error procesando la consulta: {str(e)}"
        updated_history = history + [(message, error_response)]
        return "", updated_history

def clear_chat():
    """Clear chat history"""
    global bot
    if bot:
        bot.reset_conversation()
    return []

def create_gradio_interface():
    """Create and configure Gradio interface"""
    
    # Simple interface without complex CSS to avoid compatibility issues
    with gr.Blocks(title="🏗️ Chatbot de Construcción") as iface:
        gr.Markdown("# 🏗️ Chatbot de Cotización de Construcción")
        gr.Markdown("Especialista en estimación de costos y presupuestos de obras civiles")
        
        chatbot = gr.Chatbot(
            label="Chat",
            height=400
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Escribe tu consulta sobre construcción aquí...",
                label="Mensaje",
                scale=4
            )
            submit_btn = gr.Button("📤 Enviar", scale=1)
        
        clear_btn = gr.Button("🗑️ Limpiar Chat")
        
        gr.Markdown("""
        ## 💡 Tipos de consultas:
        - 💰 Costos de construcción
        - 🧱 Materiales y cantidades  
        - 📊 Presupuestos de obras
        - 📐 Cálculos por m²
        - 🏠 Cotizaciones de edificación
        
        ## 🎯 Ejemplos:
        - "¿Cuánto cuesta construir una casa de 120m²?"
        - "Materiales para una losa de 50m²"
        - "Presupuesto para pintar 200m² de pared"
        """)
        
        # Event handlers - simplified
        def handle_message(message, history):
            if not message.strip():
                return "", history
            
            # This will be handled by the async wrapper
            return "", history
        
        def async_chat_wrapper(message, history):
            """Wrapper to handle async chat function"""
            import asyncio
            try:
                # Create or get event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run the async function
                if loop.is_running():
                    # If loop is already running, we need to use a different approach
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, chat_interface(message, history))
                        return future.result()
                else:
                    return loop.run_until_complete(chat_interface(message, history))
            except Exception as e:
                error_response = f"❌ Error: {str(e)}"
                return "", history + [(message, error_response)]
        
        submit_btn.click(
            async_chat_wrapper,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        msg.submit(
            async_chat_wrapper,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot]
        )
    
    return iface

async def launch_gradio():
    """Launch Gradio interface"""
    print("🚀 Inicializando chatbot...")
    await initialize_bot()
    print("✅ Chatbot inicializado correctamente")
    
    print("🌐 Creando interfaz web...")
    iface = create_gradio_interface()
    
    print("📡 Lanzando aplicación...")
    try:
        iface.launch(
            server_name="0.0.0.0",
            server_port=GRADIO_SERVER_PORT,
            share=False,
            debug=False,  # Reduced debug level
            show_error=True,
            quiet=False
        )
    except Exception as e:
        print(f"Error launching Gradio: {e}")
        # Try with minimal configuration
        print("Trying with minimal configuration...")
        iface.launch() 