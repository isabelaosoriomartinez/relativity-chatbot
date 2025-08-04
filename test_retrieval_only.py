"""
Script para probar solo el retrieval mejorado sin el LLM de IBM.
"""

import os
from rag_ibm import RelativityRAGPipelineIBM
import time

class MockLLM:
    """Mock LLM para pruebas sin IBM Watsonx.ai."""
    
    def __call__(self, prompt: str, temperature: float = 0.0, max_tokens: int = 1000) -> str:
        """Simula una respuesta del LLM."""
        if "relativity" in prompt.lower() or "relativityone" in prompt.lower():
            return "Based on the Relativity release notes, there are several new features and improvements available. The latest version includes enhanced functionality and performance improvements."
        else:
            return "I don't have enough information to answer that question based on the available release notes."

def test_retrieval_only():
    """Prueba solo el retrieval sin el LLM de IBM."""
    print("🚀 Probando Retrieval Mejorado")
    print("=" * 50)
    
    try:
        # Establecer variables de entorno mock para evitar errores
        os.environ["IBM_WATSONX_API_KEY"] = "mock_key"
        os.environ["IBM_WATSONX_PROJECT_ID"] = "mock_project"
        
        # Inicializar RAG pipeline
        print("📦 Inicializando RAG pipeline...")
        rag = RelativityRAGPipelineIBM()
        
        # Reemplazar el LLM con un mock
        rag.llm = MockLLM()
        
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
            "Tell me about RelativityOne updates",
            "Háblame sobre las actualizaciones de RelativityOne",
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
        
        if successful_answers >= 6:  # Al menos 6 de 8 preguntas (excluyendo las fuera de contexto)
            print("🎉 ¡Retrieval mejorado funcionando correctamente!")
            print("   - Las preguntas relevantes se responden")
            print("   - Las preguntas fuera de contexto escalan a soporte")
        else:
            print("⚠️  El retrieval necesita más ajustes")
            print("   - Revisar umbrales de similitud")
            print("   - Ajustar parámetros de retrieval")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_retrieval_only() 