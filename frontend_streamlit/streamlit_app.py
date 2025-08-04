"""
Frontend Streamlit para Relativity FAQ Chatbot.
Reemplaza el frontend Gradio con una interfaz más simple y robusta.
"""

import streamlit as st
import requests
import os
from datetime import datetime
import json

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")

# Page config
st.set_page_config(
    page_title="Relativity FAQ Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .citation {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
        font-size: 0.8rem;
    }
    .contact-form {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "contact_mode" not in st.session_state:
    st.session_state.contact_mode = False
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

def test_backend():
    """Test backend connectivity"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, str(e)

def send_message(message):
    """Send message to backend"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chatbot",
            json={"question": message},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Backend error: {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def validate_contact(name, email, organization):
    """Validate contact information"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/validate_contact",
            json={
                "name": name,
                "email": email,
                "organization": organization
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"valid": False, "error": f"Validation error: {response.status_code}"}
    except Exception as e:
        return {"valid": False, "error": f"Connection error: {str(e)}"}

def submit_contact(name, email, organization, question):
    """Submit contact information"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/collect_contact",
            json={
                "name": name,
                "email": email,
                "organization": organization,
                "question": question,
                "timestamp": datetime.now().isoformat()
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"Submission error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}

# Sidebar
with st.sidebar:
    st.title("🔧 Configuración")
    
    # Backend URL configuration
    st.subheader("Backend URL")
    backend_url = st.text_input(
        "API Base URL",
        value=API_BASE_URL,
        help="URL del backend IBM (ej: https://your-app.us-south.codeengine.appdomain.cloud)"
    )
    
    # Test backend button
    if st.button("🧪 Probar Backend"):
        with st.spinner("Probando conexión..."):
            success, result = test_backend()
            if success:
                st.success("✅ Backend conectado")
                st.json(result)
            else:
                st.error(f"❌ Error de conexión: {result}")
    
    # Environment info
    st.subheader("ℹ️ Información")
    st.write(f"**API URL:** {backend_url}")
    st.write(f"**Modo contacto:** {st.session_state.contact_mode}")

# Main content
st.title("🤖 Relativity FAQ Chatbot")
st.markdown("Pregunta sobre las notas de versión de Relativity. Si no encuentro información suficiente, te pediré tus datos de contacto.")

# Chat interface
if not st.session_state.contact_mode:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display citations if available
            if "citations" in message and message["citations"]:
                st.markdown("**📚 Fuentes:**")
                for citation in message["citations"]:
                    st.markdown(f"""
                    <div class="citation">
                        📄 {citation.get('title', 'Sin título')} - 
                        <a href="{citation.get('url', '#')}" target="_blank">{citation.get('url', 'Sin URL')}</a>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Pensando..."):
                result = send_message(prompt)
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"❌ Error: {result['error']}"
                    })
                else:
                    answer = result.get("answer", "No se pudo generar una respuesta.")
                    st.write(answer)
                    
                    # Display citations
                    citations = result.get("citations", [])
                    if citations:
                        st.markdown("**📚 Fuentes:**")
                        for citation in citations:
                            st.markdown(f"""
                            <div class="citation">
                                📄 {citation.get('title', 'Sin título')} - 
                                <a href="{citation.get('url', '#')}" target="_blank">{citation.get('url', 'Sin URL')}</a>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Add bot message to history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "citations": citations
                    })
                    
                    # Check if contact is needed
                    if result.get("needs_contact", False):
                        st.session_state.contact_mode = True
                        st.session_state.current_question = prompt
                        st.warning("⚠️ Para responder mejor a tu pregunta, necesitamos más información.")
                        st.rerun()

# Contact form
if st.session_state.contact_mode:
    st.markdown("---")
    st.markdown("### 📝 Información de Contacto")
    st.markdown("Para poder ayudarte mejor, necesitamos tus datos de contacto:")
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre completo *", placeholder="Tu nombre")
            email = st.text_input("Email *", placeholder="tu@email.com")
        
        with col2:
            organization = st.text_input("Organización *", placeholder="Tu empresa")
            phone = st.text_input("Teléfono (opcional)", placeholder="+1 234 567 8900")
        
        submitted = st.form_submit_button("📤 Enviar Información")
        
        if submitted:
            if not name or not email or not organization:
                st.error("❌ Por favor completa todos los campos obligatorios.")
            else:
                # Validate contact info
                validation = validate_contact(name, email, organization)
                
                if validation.get("valid", False):
                    # Submit contact info
                    submission = submit_contact(
                        name, email, organization, 
                        st.session_state.current_question
                    )
                    
                    if submission.get("success", False):
                        st.success("✅ ¡Gracias! Tu información ha sido registrada. Te contactaremos pronto.")
                        
                        # Add confirmation message to chat
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "✅ Tu información de contacto ha sido registrada. Te contactaremos pronto con más detalles sobre tu consulta."
                        })
                        
                        # Reset contact mode
                        st.session_state.contact_mode = False
                        st.session_state.current_question = ""
                        st.rerun()
                    else:
                        st.error(f"❌ Error al registrar: {submission.get('error', 'Error desconocido')}")
                else:
                    st.error(f"❌ Error de validación: {validation.get('error', 'Error desconocido')}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    🤖 Relativity FAQ Chatbot - Powered by IBM Watsonx.ai
</div>
""", unsafe_allow_html=True) 