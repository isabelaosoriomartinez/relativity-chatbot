"""
Script para probar las credenciales de IBM Watsonx.ai.
"""

import os
import requests
from dotenv import load_dotenv

def get_iam_token(api_key: str) -> str | None:
    """
    Obtiene un token de acceso IAM usando la API Key de IBM Cloud.
    
    Args:
        api_key: La API Key de IBM Watsonx.ai.
        
    Returns:
        El token de acceso IAM si la llamada es exitosa, None en caso contrario.
    """
    print("🔑 Obteniendo token de acceso IAM con la API Key...")
    
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                print("✅ Token de acceso IAM obtenido exitosamente.")
                return access_token
            else:
                print("❌ Error: No se encontró el token de acceso en la respuesta.")
                return None
        else:
            print(f"❌ Error al obtener el token de acceso. Código de estado: {response.status_code}")
            print(f"📄 Respuesta del servidor: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión al servicio IAM: {e}")
        return None

def test_ibm_credentials():
    """
    Prueba la conexión a la API de Watsonx.ai con las credenciales y el token de acceso IAM.
    """
    print("🔍 Probando credenciales de IBM Watsonx.ai")
    print("=" * 50)
    
    # Cargar variables de entorno del archivo .env
    load_dotenv()
    
    # Obtener credenciales
    api_key = os.getenv("IBM_WATSONX_API_KEY")
    project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
    model = os.getenv("IBM_WATSONX_MODEL", "meta-llama/llama-3-70b-instruct") # Actualizado al modelo que solicitaste
    region = os.getenv("IBM_WATSONX_REGION", "us-south")
    
    print(f"🔑 API Key: {'✅ Configurada' if api_key else '❌ Faltante'}")
    print(f"📋 Project ID: {'✅ Configurado' if project_id else '❌ Faltante'}")
    print(f"🤖 Model: {model}")
    print(f"🌍 Region: {region}")
    
    # Verificar si las credenciales necesarias están configuradas
    if not all([api_key, project_id, model, region]):
        print("\n❌ Error: Una o más credenciales están faltantes. Por favor, revisa el archivo .env.")
        return False
        
    # Paso 1: Obtener el token de acceso IAM
    access_token = get_iam_token(api_key)
    if not access_token:
        print("\n❌ No se pudo obtener el token de acceso. No se puede continuar.")
        return False
        
    # Paso 2: Probar la conexión con IBM Watsonx.ai usando el token de acceso
    print(f"\n🌐 Probando conexión con IBM Watsonx.ai...")
    
    try:
        url = f"https://{region}.ml.cloud.ibm.com/ml/v1-beta/generation/text?version=2024-05-29" # Usando la versión beta
        headers = {
            "Authorization": f"Bearer {access_token}",  # USAR EL TOKEN DE ACCESO
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # El payload debe incluir el 'project_id' y el 'model_id'
        payload = {
            "model_id": model,
            "input": "Write a short and friendly welcome message.",
            "parameters": {
                "temperature": 0.0,
                "max_new_tokens": 50
            },
            "project_id": project_id
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("results", [{}])[0].get("generated_text", "")
            print(f"\n✅ Conexión exitosa a Watsonx.ai!")
            print(f"📝 Respuesta de prueba: {generated_text.strip()[:100]}...")
            return True
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            print(f"📄 Respuesta de la API: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error de conexión con Watsonx.ai: {e}")
        return False

def add_project_id():
    """Agrega el IBM_WATSONX_PROJECT_ID al archivo .env si falta."""
    print("\n🔧 Configurando IBM_WATSONX_PROJECT_ID...")
    
    try:
        # Intenta leer el archivo .env actual
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        # Si no existe, crea uno vacío
        print("💡 Creando archivo .env...")
        content = ""
    
    # Verificar si ya existe IBM_WATSONX_PROJECT_ID
    if "IBM_WATSONX_PROJECT_ID" in content:
        print("✅ IBM_WATSONX_PROJECT_ID ya está configurado.")
        return True
    
    # Solicitar el Project ID
    print("📋 Por favor, ingresa tu IBM_WATSONX_PROJECT_ID:")
    print("💡 Puedes encontrarlo en la página de tu proyecto en Watsonx.ai.")
    project_id = input("Project ID: ").strip()
    
    if not project_id:
        print("❌ Project ID no puede estar vacío.")
        return False
    
    # Agregar al archivo .env
    new_line = f"IBM_WATSONX_PROJECT_ID={project_id}\n"
    
    try:
        with open('.env', 'a', encoding='utf-8') as f:
            f.write(new_line)
        print("✅ IBM_WATSONX_PROJECT_ID agregado al archivo .env.")
        return True
    except Exception as e:
        print(f"❌ Error al escribir en .env: {e}")
        return False

if __name__ == "__main__":
    # Primero, agregar Project ID si falta
    load_dotenv()
    if not os.getenv("IBM_WATSONX_PROJECT_ID"):
        if add_project_id():
            # Recargar las variables de entorno después de escribir en el archivo
            load_dotenv(override=True)
        else:
            print("❌ No se pudo configurar el Project ID.")
            exit(1)
    
    # Probar las credenciales con el nuevo flujo
    if test_ibm_credentials():
        print("\n🎉 ¡Credenciales configuradas correctamente!")
        print("🚀 Ya puedes usar el RAG con IBM Watsonx.ai.")
    else:
        print("\n❌ Error en la configuración de credenciales.")
        print("🔧 Revisa tu API Key y Project ID, e inténtalo de nuevo.")

