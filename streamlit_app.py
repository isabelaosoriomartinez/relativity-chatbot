"""
Frontend Streamlit para Relativity FAQ Chatbot.
Reemplaza el frontend Gradio con una interfaz más simple y robusta.
"""

import streamlit as st
import requests
import json
import os
from typing import Dict, Any, List
from datetime import datetime

# Configuración
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000").rstrip("/")

# Configurar página
st.set_page_config(
    page_title="Relativity Releases FAQ Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def test_backend_health():
    """Prueba la conexión con el backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def send_chat_message(message: str) -> Dict[str, Any]:
    """Envía un mensaje al backend y retorna la respuesta."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/chatbot",
            json={"question": message},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"Error del servidor: {response.status_code}",
                "has_sufficient_info": False,
                "needs_contact": False
            }
    except requests.exceptions.ConnectionError:
        return {
            "error": "No se puede conectar al backend. Verifica que esté ejecutándose.",
            "has_sufficient_info": False,
            "needs_contact": False
        }
    except Exception as e:
        return {
            "error": f"Error inesperado: {str(e)}",
            "has_sufficient_info": False,
            "needs_contact": False
        }

def collect_contact_info(name: str, email: str, organization: str, original_question: str) -> Dict[str, Any]:
    """Envía información de contacto al backend."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/collect_contact",
            json={
                "name": name,
                "email": email,
                "organization": organization,
                "original_question": original_question
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Error: {str(e)}"}

def format_citations(citations: List[Dict[str, str]]) -> str:
    """Formatea las citaciones para mostrar."""
    if not citations:
        return ""
    
    formatted = "\n\n**📚 Fuentes:**\n"
    for i, citation in enumerate(citations, 1):
        title = citation.get("title") or citation.get("heading") or "Fuente"
        url = citation.get("url") or "#"
        formatted += f"{i}. [{title}]({url})\n"
    
    return formatted

def main():
    """Función principal de la aplicación."""
    
    # Sidebar
    with st.sidebar:
        st.title("🔧 Configuración")
        
        # Test backend
        if st.button("🧪 Test Backend (/health)"):
            with st.spinner("Probando conexión..."):
                success, result = test_backend_health()
                if success:
                    st.success("✅ Backend conectado")
                    st.json(result)
                else:
                    st.error("❌ Error de conexión")
                    st.text(result)
        
        st.divider()
        
        # Información del sistema
        st.subheader("ℹ️ Información")
        st.text(f"Backend: {BACKEND_URL}")
        st.text(f"Estado: {'🟢 Conectado' if test_backend_health()[0] else '🔴 Desconectado'}")
        
        # Limpiar chat
        if st.button("🗑️ Limpiar Chat"):
            st.session_state.messages = []
            st.session_state.contact_mode = False
            st.session_state.pending_question = ""
            st.rerun()
    
    # Título principal
    st.title("🤖 Relativity Releases FAQ Chatbot")
    st.markdown("Haz preguntas sobre las versiones de Relativity y obtén respuestas basadas en la documentación oficial.")
    
    # Inicializar session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "contact_mode" not in st.session_state:
        st.session_state.contact_mode = False
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = ""
    
    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Modo de recolección de contacto
    if st.session_state.contact_mode:
        st.info("📝 Por favor proporciona tu información de contacto para que nuestro equipo pueda ayudarte.")
        
        with st.form("contact_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre completo", key="contact_name")
                email = st.text_input("Correo electrónico", key="contact_email")
            with col2:
                organization = st.text_input("Organización", key="contact_org")
                st.text_area("Pregunta original", value=st.session_state.pending_question, disabled=True)
            
            submitted = st.form_submit_button("📤 Enviar información de contacto")
            
            if submitted:
                if name and email and organization:
                    with st.spinner("Enviando información..."):
                        result = collect_contact_info(name, email, organization, st.session_state.pending_question)
                    
                    if result.get("success"):
                        st.success("✅ Información enviada correctamente. Nuestro equipo se pondrá en contacto contigo en 24-48 horas.")
                        st.session_state.contact_mode = False
                        st.session_state.pending_question = ""
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                else:
                    st.error("❌ Por favor completa todos los campos.")
    
    # Chat input
    if not st.session_state.contact_mode:
        if prompt := st.chat_input("Escribe tu pregunta aquí..."):
            # Agregar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Mostrar mensaje del usuario
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Obtener respuesta del backend
            with st.chat_message("assistant"):
                with st.spinner("🤔 Pensando..."):
                    response = send_chat_message(prompt)
                
                if "error" in response:
                    st.error(response["error"])
                    st.session_state.messages.append({"role": "assistant", "content": f"❌ Error: {response['error']}"})
                else:
                    answer = response.get("answer", "No se pudo generar una respuesta.")
                    citations = response.get("citations", [])
                    
                    # Formatear respuesta completa
                    full_response = answer + format_citations(citations)
                    st.markdown(full_response)
                    
                    # Agregar respuesta al historial
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # Si necesita contacto, activar modo contacto
                    if response.get("needs_contact", False):
                        st.session_state.contact_mode = True
                        st.session_state.pending_question = prompt
                        st.info("📝 El sistema necesita más información para responder tu pregunta. Por favor proporciona tus datos de contacto.")
                        st.rerun()

if __name__ == "__main__":
    main() 