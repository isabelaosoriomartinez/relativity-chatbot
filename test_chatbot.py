"""
Script de prueba para verificar que el chatbot funciona correctamente.
"""

import requests
import json
import time

def test_backend():
    """Prueba el backend Flask."""
    print("🔍 Probando backend...")
    
    # Prueba health endpoint
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend saludable: {health_data}")
        else:
            print(f"❌ Backend no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False
    
    # Prueba chatbot endpoint
    try:
        test_question = "What are the new features in Relativity?"
        response = requests.post(
            "http://127.0.0.1:5000/chatbot",
            json={"question": test_question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chatbot responde correctamente:")
            print(f"   - Pregunta: {test_question}")
            print(f"   - Respuesta: {result.get('answer', 'Sin respuesta')}")
            print(f"   - Tiene info suficiente: {result.get('has_sufficient_info', False)}")
            return True
        else:
            print(f"❌ Error en chatbot endpoint: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando chatbot: {e}")
        return False

def test_frontend():
    """Prueba el frontend Streamlit."""
    print("\n🔍 Probando frontend...")
    
    try:
        response = requests.get("http://127.0.0.1:8501")
        if response.status_code == 200:
            print("✅ Frontend accesible")
            return True
        else:
            print(f"❌ Frontend no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al frontend: {e}")
        return False

def main():
    """Ejecuta todas las pruebas."""
    print("🚀 Pruebas del Relativity FAQ Chatbot")
    print("=" * 50)
    
    # Esperar un poco para que los servicios se inicien
    print("⏳ Esperando que los servicios se inicien...")
    time.sleep(2)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 50)
    print("📊 Resultados de las pruebas:")
    print(f"   Backend: {'✅ OK' if backend_ok else '❌ FALLO'}")
    print(f"   Frontend: {'✅ OK' if frontend_ok else '❌ FALLO'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 ¡Todo funciona correctamente!")
        print("\n🌐 URLs:")
        print("   - Backend: http://127.0.0.1:5000")
        print("   - Frontend: http://127.0.0.1:8501")
        print("\n💡 Puedes abrir http://127.0.0.1:8501 en tu navegador para usar el chatbot.")
    else:
        print("\n⚠️  Algunos servicios no están funcionando correctamente.")
        print("   Verifica que ambos servicios estén ejecutándose:")
        print("   - Backend: python app.py")
        print("   - Frontend: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main() 