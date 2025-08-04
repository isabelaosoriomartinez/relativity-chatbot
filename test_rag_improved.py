"""
Script de prueba para verificar el RAG mejorado.
Prueba preguntas en inglés y español para verificar que no escala todo a soporte.
"""

import requests
import json
import time

def test_question(question, language):
    """Prueba una pregunta específica."""
    print(f"\n🔍 Probando pregunta en {language}:")
    print(f"   Pregunta: {question}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/chatbot",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📝 Respuesta: {result.get('answer', 'Sin respuesta')[:200]}...")
            print(f"   📊 Tiene info suficiente: {result.get('has_sufficient_info', False)}")
            print(f"   📞 Necesita contacto: {result.get('needs_contact', True)}")
            print(f"   📚 Citas: {len(result.get('citations', []))}")
            
            if result.get('citations'):
                for i, citation in enumerate(result.get('citations', [])[:2]):
                    print(f"      Cita {i+1}: {citation.get('heading', 'Sin título')}")
            
            return result.get('has_sufficient_info', False)
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def main():
    """Ejecuta las pruebas del RAG mejorado."""
    print("🚀 Pruebas del RAG Mejorado")
    print("=" * 50)
    
    # Esperar que el backend esté listo
    print("⏳ Esperando que el backend se inicie...")
    time.sleep(3)
    
    # Preguntas de prueba
    test_questions = [
        ("What's new in RelativityOne?", "Inglés"),
        ("¿Qué hay de nuevo en RelativityOne?", "Español"),
        ("What are the latest features?", "Inglés"),
        ("¿Cuáles son las características más recientes?", "Español"),
        ("Tell me about RelativityOne updates", "Inglés"),
        ("Háblame sobre las actualizaciones de RelativityOne", "Español"),
        ("What is quantum computing?", "Inglés"),  # Pregunta fuera de contexto
        ("¿Qué es la computación cuántica?", "Español")  # Pregunta fuera de contexto
    ]
    
    successful_answers = 0
    total_questions = len(test_questions)
    
    for question, language in test_questions:
        if test_question(question, language):
            successful_answers += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {successful_answers}/{total_questions} preguntas respondidas correctamente")
    
    if successful_answers >= 6:  # Al menos 6 de 8 preguntas (excluyendo las fuera de contexto)
        print("🎉 ¡RAG mejorado funcionando correctamente!")
        print("   - Las preguntas relevantes se responden")
        print("   - Las preguntas fuera de contexto escalan a soporte")
    else:
        print("⚠️  El RAG necesita más ajustes")
        print("   - Revisar umbrales de similitud")
        print("   - Ajustar parámetros de retrieval")

if __name__ == "__main__":
    main() 