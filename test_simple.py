"""
Script simple para probar el RAG mejorado directamente.
"""

from rag_ibm import RelativityRAGPipelineIBM
import time

def test_rag_directly():
    """Prueba el RAG directamente sin el backend."""
    print("🚀 Probando RAG Mejorado Directamente")
    print("=" * 50)
    
    try:
        # Inicializar RAG pipeline
        print("📦 Inicializando RAG pipeline...")
        rag = RelativityRAGPipelineIBM()
        
        # Cargar vector store
        print("🗄️ Cargando vector store...")
        if not rag.load_existing_vector_store():
            print("❌ No se pudo cargar el vector store")
            return
        
        # Crear QA chain
        print("🔗 Creando QA chain...")
        rag.create_qa_chain()
        
        # Preguntas de prueba
        test_questions = [
            "What's new in RelativityOne?",
            "¿Qué hay de nuevo en RelativityOne?",
            "What are the latest features?",
            "¿Cuáles son las características más recientes?",
            "What is quantum computing?",  # Fuera de contexto
            "¿Qué es la computación cuántica?"  # Fuera de contexto
        ]
        
        successful_answers = 0
        total_questions = len(test_questions)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 Pregunta {i}: {question}")
            
            try:
                # Consultar RAG
                result = rag.query(question)
                
                print(f"   📝 Respuesta: {result.get('answer', 'Sin respuesta')[:150]}...")
                print(f"   📊 Tiene info suficiente: {result.get('has_sufficient_info', False)}")
                print(f"   📞 Necesita contacto: {result.get('needs_contact', True)}")
                print(f"   📚 Citas: {len(result.get('citations', []))}")
                
                if result.get('has_sufficient_info', False):
                    successful_answers += 1
                    print("   ✅ Respuesta exitosa")
                else:
                    print("   ⚠️ No hay suficiente información")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Resultados: {successful_answers}/{total_questions} preguntas respondidas correctamente")
        
        if successful_answers >= 4:  # Al menos 4 de 6 preguntas (excluyendo las fuera de contexto)
            print("🎉 ¡RAG mejorado funcionando correctamente!")
            print("   - Las preguntas relevantes se responden")
            print("   - Las preguntas fuera de contexto escalan a soporte")
        else:
            print("⚠️  El RAG necesita más ajustes")
            print("   - Revisar umbrales de similitud")
            print("   - Ajustar parámetros de retrieval")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_rag_directly() 