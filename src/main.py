#!/usr/bin/env python3
"""
Main entry point for Construction Cost Estimation Chatbot
"""
import asyncio
from .construction_bot import ConstructionCostBot
from .gradio_interface import launch_gradio

async def run_cli():
    """Run the command line interface"""
    bot = ConstructionCostBot()
    await bot.initialize()
    
    print("🏗️ Chatbot de Cotización de Construcción con Historial")
    print("=" * 50)
    print("Comandos especiales:")
    print("  'quit' - Salir del programa")
    print("  'history' - Ver historial de conversación")
    print("  'clear' - Limpiar historial")
    print("  'help' - Mostrar esta ayuda")
    print()
    
    while True:
        try:
            question = input("💬 Pregunta: ").strip()
            
            if question.lower() == 'quit':
                break
            elif question.lower() == 'history':
                bot.show_history()
                continue
            elif question.lower() == 'clear':
                bot.clear_history()
                continue
            elif question.lower() == 'help':
                print("📋 Comandos disponibles:")
                print("  'quit' - Salir del programa")
                print("  'history' - Ver historial de conversación")
                print("  'clear' - Limpiar historial")
                print("  'help' - Mostrar esta ayuda")
                print("  Cualquier otra cosa - Hacer una pregunta sobre construcción")
                continue
            elif not question:
                continue
            
            print("🤖 Procesando...")
            response = await bot.ask(question)
            print(f"📋 Respuesta: {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main function for command line and web interface selection"""
    choice = input("¿Cómo quieres ejecutar el chatbot?\n1. 💻 Línea de comandos\n2. 🌐 Interfaz web (Gradio)\nElige (1/2): ").strip()
    
    if choice == "2":
        await launch_gradio()
    else:
        await run_cli()

if __name__ == "__main__":
    asyncio.run(main()) 