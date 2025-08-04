"""
Script para probar el backend Flask con el RAG real.
"""

import requests
import json
import time

def test_backend():
    """Prueba el backend Flask con preguntas reales."""
    print("🚀 Probando Backend Flask con RAG Real")
    print("=" * 50)
    
    # URL del backend
    base_url = "http://127.0.0.1:5000"
    
    # Preguntas de prueba
    test_questions = [
        "What are the new features in RelativityOne?",
        "¿Cuáles son las nuevas características en RelativityOne?",
        "Tell me about the latest RelativityOne release",
        "What is quantum computing?"  # Fuera de contexto
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Pregunta {i}: {question}")
        
        try:
            # Preparar la petición
            payload = {"question": question}
            
            # Hacer la petición
            start_time = time.time()
            response = requests.post(
                f"{base_url}/chatbot",
                json=payload,
                timeout=60
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   ⏱️  Tiempo: {response_time:.2f}s")
                print(f"   📝 Respuesta: {result.get('answer', 'Sin respuesta')[:200]}...")
                print(f"   📊 Suficiente info: {result.get('has_sufficient_info', False)}")
                print(f"   📞 Necesita contacto: {result.get('needs_contact', True)}")
                print(f"   📚 Citas: {len(result.get('citations', []))}")
                
                if result.get('citations'):
                    for j, citation in enumerate(result.get('citations', [])[:2]):
                        print(f"      📖 Cita {j+1}: {citation.get('heading', 'Sin título')}")
                
                if result.get('has_sufficient_info', False):
                    print("   ✅ Respuesta exitosa")
                else:
                    print("   ⚠️ No hay suficiente información")
                    
            else:
                print(f"   ❌ Error HTTP {response.status_code}")
                print(f"   📄 Respuesta: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Error: No se puede conectar al backend")
            print("   💡 Asegúrate de que el backend esté ejecutándose: python app.py")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_health():
    """Prueba el endpoint de salud."""
    print("\n🏥 Probando endpoint /health...")
    
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backend saludable: {result}")
            return True
        else:
            print(f"❌ Error en health check: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

if __name__ == "__main__":
    # Primero probar health check
    if test_health():
        # Si el backend está funcionando, probar el chatbot
        test_backend()
    else:
        print("\n❌ El backend no está disponible")
        print("💡 Ejecuta: python app.py") 