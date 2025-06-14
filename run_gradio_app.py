#!/usr/bin/env python3
"""
Launcher script for Construction Cost Estimation Gradio App
"""
import sys
import subprocess
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'gradio',
        'langchain',
        'langchain_openai',
        'langchain_mcp_adapters',
        'langgraph'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Paquetes faltantes:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n💡 Para instalar las dependencias:")
        print("   pip install -r requirements_gradio.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🚀 Iniciando Chatbot de Construcción con Gradio")
    print("-" * 50)
    
    # Check if required files exist
    required_files = ['construction_chatbot.py', 'gradio_app.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Archivo requerido no encontrado: {file}")
            return 1
    
    # Check dependencies
    print("🔍 Verificando dependencias...")
    if not check_dependencies():
        return 1
    
    print("✅ Todas las dependencias están instaladas")
    
    # Check API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("⚠️ ADVERTENCIA: OPENAI_API_KEY no encontrada en variables de entorno")
        print("   La aplicación intentará usar la clave hardcodeada en construction_chatbot.py")
    
    print("\n🌐 Iniciando servidor Gradio...")
    print("📱 La aplicación estará disponible en: http://localhost:7860")
    print("🛑 Presiona Ctrl+C para detener la aplicación")
    print("-" * 50)
    
    try:
        # Import and run the gradio app
        from gradio_app import demo
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
        return 0
    except Exception as e:
        print(f"\n❌ Error ejecutando la aplicación: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 