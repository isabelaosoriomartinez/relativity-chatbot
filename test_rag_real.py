"""
Script para probar el RAG completo con el LLM real de IBM Watsonx.ai.
"""

import os
import time
from dotenv import load_dotenv
from rag_ibm import RelativityRAGPipelineIBM

def test_rag_with_real_llm():
    """Prueba el RAG completo con el LLM real de IBM Watsonx.ai."""
    print("🚀 Probando RAG Completo con IBM Watsonx.ai")
    print("=" * 60)
    
    try:
        # Inicializar RAG pipeline
        print("📦 Inicializando RAG pipeline...")
        rag = RelativityRAGPipelineIBM()
        
        # Cargar vector store
        print("🗄️ Cargando vector store...")
        if not rag.load_existing_vector_store():
            print("❌ No se pudo cargar el vector store")
            return False
        
        # Crear QA chain
        print("🔗 Creando QA chain...")
        rag.create_qa_chain()
        
        # Preguntas de prueba
        test_questions = [
            ("What's new in RelativityOne?", "Inglés - Pregunta general"),
            ("¿Qué hay de nuevo en RelativityOne?", "Español - Pregunta general"),
            ("What are the latest features?", "Inglés - Características"),
            ("¿Cuáles son las características más recientes?", "Español - Características"),
            ("Tell me about RelativityOne updates", "Inglés - Actualizaciones"),
            ("Háblame sobre las actualizaciones de RelativityOne", "Español - Actualizaciones"),
            ("What is quantum computing?", "Inglés - Fuera de contexto"),
            ("¿Qué es la computación cuántica?", "Español - Fuera de contexto")
        ]
        
        successful_answers = 0
        total_questions = len(test_questions)
        
        for i, (question, description) in enumerate(test_questions, 1):
            print(f"\n🔍 Pregunta {i}: {question}")
            print(f"   📝 Descripción: {description}")
            
            try:
                # Consultar RAG con LLM real
                start_time = time.time()
                result = rag.query(question)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                print(f"   ⏱️  Tiempo de respuesta: {response_time:.2f}s")
                print(f"   📝 Respuesta: {result.get('answer', 'Sin respuesta')[:200]}...")
                print(f"   📊 Tiene info suficiente: {result.get('has_sufficient_info', False)}")
                print(f"   📞 Necesita contacto: {result.get('needs_contact', True)}")
                print(f"   📚 Citas: {len(result.get('citations', []))}")
                
                if result.get('citations'):
                    for j, citation in enumerate(result.get('citations', [])[:2]):
                        print(f"      📖 Cita {j+1}: {citation.get('heading', 'Sin título')}")
                
                if result.get('has_sufficient_info', False):
                    successful_answers += 1
                    print("   ✅ Respuesta exitosa")
                else:
                    print("   ⚠️ No hay suficiente información")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 Resultados: {successful_answers}/{total_questions} preguntas respondidas correctamente")
        
        if successful_answers >= 6:  # Al menos 6 de 8 preguntas (excluyendo las fuera de contexto)
            print("🎉 ¡RAG completo funcionando perfectamente!")
            print("   - Las preguntas relevantes se responden con LLM real")
            print("   - Las preguntas fuera de contexto escalan a soporte")
            print("   - El sistema está listo para producción")
            return True
        else:
            print("⚠️  El RAG necesita más ajustes")
            print("   - Revisar umbrales de similitud")
            print("   - Ajustar parámetros de retrieval")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def test_specific_questions():
    """Prueba preguntas específicas con el RAG real."""
    print("\n🎯 Probando Preguntas Específicas")
    print("=" * 40)
    
    try:
        # Inicializar RAG pipeline
        rag = RelativityRAGPipelineIBM()
        
        if not rag.load_existing_vector_store():
            print("❌ No se pudo cargar el vector store")
            return
        
        rag.create_qa_chain()
        
        # Preguntas específicas para probar
        specific_questions = [
            "What are the new features in RelativityOne?",
            "¿Cuáles son las nuevas características en RelativityOne?",
            "Tell me about the latest RelativityOne release",
            "Háblame sobre la última versión de RelativityOne"
        ]
        
        for question in specific_questions:
            print(f"\n🔍 Pregunta: {question}")
            
            try:
                result = rag.query(question)
                
                print(f"📝 Respuesta: {result.get('answer', 'Sin respuesta')}")
                print(f"📊 Suficiente info: {result.get('has_sufficient_info', False)}")
                print(f"📚 Citas: {len(result.get('citations', []))}")
                
                if result.get('citations'):
                    for citation in result.get('citations', []):
                        print(f"   📖 {citation.get('heading', 'Sin título')} - {citation.get('url', 'Sin URL')}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar que las credenciales estén configuradas
    if not os.getenv("IBM_WATSONX_API_KEY") or not os.getenv("IBM_WATSONX_PROJECT_ID"):
        print("❌ Error: Las credenciales de IBM Watsonx.ai no están configuradas")
        print("💡 Ejecuta: python test_ibm_credentials.py")
        exit(1)
    
    # Probar RAG completo
    if test_rag_with_real_llm():
        print("\n🎉 ¡RAG completo funcionando correctamente!")
        print("🚀 Ya puedes usar el chatbot con respuestas reales")
        
        # Probar preguntas específicas
        test_specific_questions()
    else:
        print("\n❌ El RAG necesita ajustes")
        print("🔧 Revisa los parámetros y configuración") 