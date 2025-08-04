"""
Script para configurar credenciales de IBM Watsonx.ai
"""

import os
import getpass

def setup_ibm_credentials():
    """Configura las credenciales de IBM Watsonx.ai."""
    print("🔧 Configuración de IBM Watsonx.ai")
    print("=" * 50)
    
    print("\n📋 Para obtener tus credenciales:")
    print("1. Ve a: https://cloud.ibm.com")
    print("2. Inicia sesión con: 1113699395@u.icesi.edu.co")
    print("3. Ve a Watsonx.ai: https://dataplatform.cloud.ibm.com/wx/home")
    print("4. Crea un proyecto o usa uno existente")
    print("5. Obtén la API Key desde tu perfil → API Keys")
    print("6. Obtén el Project ID desde Settings del proyecto")
    
    print("\n🔑 Ingresa tus credenciales:")
    
    # Solicitar credenciales
    api_key = getpass.getpass("API Key: ")
    project_id = input("Project ID: ")
    
    if api_key and project_id:
        # Configurar variables de entorno
        os.environ['IBM_WATSONX_API_KEY'] = api_key
        os.environ['IBM_WATSONX_PROJECT_ID'] = project_id
        
        print("\n✅ Credenciales configuradas temporalmente")
        print("💡 Para hacerlas permanentes, crea un archivo .env con:")
        print(f"IBM_WATSONX_API_KEY={api_key}")
        print(f"IBM_WATSONX_PROJECT_ID={project_id}")
        
        return True
    else:
        print("\n❌ Credenciales incompletas")
        return False

def test_credentials():
    """Prueba las credenciales configuradas."""
    print("\n🧪 Probando credenciales...")
    
    api_key = os.getenv('IBM_WATSONX_API_KEY')
    project_id = os.getenv('IBM_WATSONX_PROJECT_ID')
    
    if not api_key or api_key == "your_api_key_here":
        print("❌ API Key no configurada")
        return False
    
    if not project_id or project_id == "your_project_id_here":
        print("❌ Project ID no configurado")
        return False
    
    print("✅ Credenciales configuradas")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   Project ID: {project_id}")
    
    return True

if __name__ == "__main__":
    if not test_credentials():
        setup_ibm_credentials()
    
    print("\n🚀 Para probar el chatbot:")
    print("1. Reinicia el backend: python app.py")
    print("2. Abre el frontend: http://127.0.0.1:7860")
    print("3. Haz una pregunta como 'Que hay de nuevo?'") 