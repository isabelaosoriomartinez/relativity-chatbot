"""
Script de prueba final para verificar la migración a Streamlit.
"""

import requests
import time
import os

def test_backend():
    """Prueba el backend Flask."""
    print("🔍 Probando backend Flask...")
    
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend saludable: {health_data}")
            return True
        else:
            print(f"❌ Backend no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def test_streamlit():
    """Prueba el frontend Streamlit."""
    print("\n🔍 Probando frontend Streamlit...")
    
    try:
        response = requests.get("http://127.0.0.1:8501", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend Streamlit accesible")
            return True
        else:
            print(f"❌ Frontend no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al frontend: {e}")
        return False

def test_chatbot():
    """Prueba el endpoint del chatbot."""
    print("\n🔍 Probando chatbot endpoint...")
    
    try:
        test_question = "what's the new?"
        response = requests.post(
            "http://127.0.0.1:5000/chatbot",
            json={"question": test_question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chatbot responde correctamente:")
            print(f"   - Pregunta: {test_question}")
            print(f"   - Respuesta: {result.get('answer', 'Sin respuesta')[:100]}...")
            print(f"   - Tiene info suficiente: {result.get('has_sufficient_info', False)}")
            print(f"   - Necesita contacto: {result.get('needs_contact', False)}")
            return True
        else:
            print(f"❌ Error en chatbot endpoint: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando chatbot: {e}")
        return False

def main():
    """Ejecuta todas las pruebas de migración."""
    print("🚀 Pruebas de Migración a Streamlit")
    print("=" * 50)
    
    # Esperar que los servicios se inicien
    print("⏳ Esperando que los servicios se inicien...")
    time.sleep(3)
    
    # Ejecutar pruebas
    backend_ok = test_backend()
    streamlit_ok = test_streamlit()
    chatbot_ok = test_chatbot()
    
    print("\n" + "=" * 50)
    print("📊 Resultados de la migración:")
    print(f"   Backend Flask: {'✅ OK' if backend_ok else '❌ FALLO'}")
    print(f"   Frontend Streamlit: {'✅ OK' if streamlit_ok else '❌ FALLO'}")
    print(f"   Chatbot endpoint: {'✅ OK' if chatbot_ok else '❌ FALLO'}")
    
    if backend_ok and streamlit_ok and chatbot_ok:
        print("\n🎉 ¡Migración exitosa!")
        print("\n🌐 URLs:")
        print("   - Backend API: http://127.0.0.1:5000")
        print("   - Frontend Streamlit: http://127.0.0.1:8501")
        print("\n💡 Instrucciones:")
        print("   1. Abre http://127.0.0.1:8501 en tu navegador")
        print("   2. Haz una pregunta como 'what's the new?'")
        print("   3. Usa el botón 'Test Backend' en la sidebar para verificar la conexión")
    else:
        print("\n⚠️  Algunos servicios no están funcionando.")
        print("\n🔧 Solución:")
        print("   1. Terminal 1: python app.py")
        print("   2. Terminal 2: python -m streamlit run streamlit_app.py")

if __name__ == "__main__":
    main() 