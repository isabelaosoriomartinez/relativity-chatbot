"""
Script para configurar las credenciales de IBM Watsonx.ai.
"""

import os
from dotenv import load_dotenv

def setup_ibm_credentials():
    """Guía para configurar las credenciales de IBM Watsonx.ai."""
    print("🔧 Configuración de IBM Watsonx.ai")
    print("=" * 50)
    
    print("📋 Para obtener las credenciales de IBM Watsonx.ai:")
    print("1. Ve a https://cloud.ibm.com/")
    print("2. Inicia sesión con tu cuenta de IBM")
    print("3. Ve a 'Watsonx.ai' en el menú")
    print("4. Crea un nuevo proyecto o usa uno existente")
    print("5. En el proyecto, ve a 'Manage' > 'Access (IAM)'")
    print("6. Crea una nueva API Key o usa una existente")
    print("7. Copia el Project ID y la API Key")
    
    print("\n🔑 Información necesaria:")
    print("- IBM_WATSONX_API_KEY: Tu API Key de IBM Cloud")
    print("- IBM_WATSONX_PROJECT_ID: El ID de tu proyecto de Watsonx.ai")
    
    # Verificar configuración actual
    load_dotenv()
    current_api_key = os.getenv("IBM_WATSONX_API_KEY")
    current_project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
    
    print(f"\n📊 Configuración actual:")
    print(f"   API Key: {'✅ Configurada' if current_api_key else '❌ Faltante'}")
    print(f"   Project ID: {'✅ Configurado' if current_project_id else '❌ Faltante'}")
    
    if current_api_key and current_project_id:
        print("\n💡 Para actualizar las credenciales:")
        print("1. Edita el archivo .env")
        print("2. Reemplaza los valores actuales")
        print("3. Ejecuta: python test_ibm_credentials.py")
        
        # Opción para actualizar
        update = input("\n¿Quieres actualizar las credenciales? (s/n): ").lower().strip()
        if update == 's':
            update_credentials()
    else:
        print("\n❌ Faltan credenciales. Sigue los pasos arriba para configurarlas.")

def update_credentials():
    """Actualiza las credenciales en el archivo .env."""
    print("\n🔄 Actualizando credenciales...")
    
    # Leer el archivo .env actual
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ Archivo .env no encontrado")
        return
    
    # Solicitar nuevas credenciales
    print("\n📝 Ingresa las nuevas credenciales:")
    new_api_key = input("Nueva API Key: ").strip()
    new_project_id = input("Nuevo Project ID: ").strip()
    
    if not new_api_key or not new_project_id:
        print("❌ Las credenciales no pueden estar vacías")
        return
    
    # Actualizar líneas
    updated_lines = []
    for line in lines:
        if line.startswith("IBM_WATSONX_API_KEY="):
            updated_lines.append(f"IBM_WATSONX_API_KEY={new_api_key}\n")
        elif line.startswith("IBM_WATSONX_PROJECT_ID="):
            updated_lines.append(f"IBM_WATSONX_PROJECT_ID={new_project_id}\n")
        else:
            updated_lines.append(line)
    
    # Escribir archivo actualizado
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        print("✅ Credenciales actualizadas en .env")
        print("🧪 Ejecuta 'python test_ibm_credentials.py' para probar")
    except Exception as e:
        print(f"❌ Error al actualizar .env: {e}")

def show_current_config():
    """Muestra la configuración actual."""
    load_dotenv()
    
    print("📊 Configuración actual de IBM Watsonx.ai:")
    print("=" * 40)
    
    config = {
        "API Key": os.getenv("IBM_WATSONX_API_KEY", "No configurada"),
        "Project ID": os.getenv("IBM_WATSONX_PROJECT_ID", "No configurado"),
        "Model": os.getenv("IBM_WATSONX_MODEL", "meta-llama/llama-2-70b-chat"),
        "Region": os.getenv("IBM_WATSONX_REGION", "us-south")
    }
    
    for key, value in config.items():
        if "Key" in key and value != "No configurada":
            # Ocultar parte de la API key por seguridad
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"   {key}: {masked_value}")
        else:
            print(f"   {key}: {value}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_current_config()
    else:
        setup_ibm_credentials() 