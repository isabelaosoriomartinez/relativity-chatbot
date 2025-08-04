# Relativity FAQ Chatbot - MVP

Chatbot inteligente para responder preguntas sobre las notas de versión de Relativity usando IBM Watsonx.ai.

## 🏗️ Arquitectura

El proyecto está separado en dos componentes independientes:

### Frontend (Streamlit)
- **Ubicación**: `frontend_streamlit/`
- **Tecnología**: Streamlit
- **Despliegue**: Streamlit Cloud, Heroku, o cualquier hosting
- **Dependencias**: Mínimas (solo `streamlit` y `requests`)

### Backend (IBM)
- **Ubicación**: `backend_ibm/`
- **Tecnología**: Flask + IBM Watsonx.ai
- **Despliegue**: IBM Code Engine, Cloud Foundry
- **Dependencias**: Complejas (LangChain, ChromaDB, IBM Watson)

## 🚀 Despliegue Rápido

### 1. Backend IBM

```bash
cd backend_ibm
# Configurar variables de entorno
export IBM_WATSONX_API_KEY=your_api_key
export IBM_WATSONX_PROJECT_ID=your_project_id
export GOOGLE_SHEETS_CREDENTIALS=your_credentials_json

# Desplegar en IBM Code Engine
ibmcloud ce app create --name relativity-backend --source .
```

### 2. Frontend Streamlit

```bash
cd frontend_streamlit
# Configurar URL del backend
export API_BASE_URL=https://your-backend-url.codeengine.appdomain.cloud

# Desplegar en Streamlit Cloud
# Subir a GitHub y conectar con share.streamlit.io
```

## 🔧 Desarrollo Local

### Backend
```bash
cd backend_ibm
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend_streamlit
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📋 Características

### 🤖 Chatbot Inteligente
- Respuestas basadas en RAG (Retrieval-Augmented Generation)
- Citas automáticas con URLs y títulos
- Soporte multilingüe (ES/EN)
- Prevención de alucinaciones

### 📝 Gestión de Contactos
- Formulario de contacto cuando no hay información suficiente
- Validación de datos
- Integración con Google Sheets
- Timestamp automático

### 🔗 Arquitectura Separada
- Frontend y backend independientes
- Comunicación vía HTTP REST
- Escalabilidad independiente
- Despliegue flexible

## 🛠️ Tecnologías

### Backend
- **Flask**: API REST
- **LangChain**: Pipeline RAG
- **ChromaDB**: Vector store
- **IBM Watsonx.ai**: LLM (Llama 2/3, Mistral)
- **Google Sheets API**: Logging de contactos

### Frontend
- **Streamlit**: UI interactiva
- **Requests**: Comunicación HTTP
- **CSS personalizado**: Estilos modernos

## 📊 Monitoreo

### Backend
- Health check: `GET /health`
- Logs: `ibmcloud ce app logs --name relativity-backend`

### Frontend
- Estado de conexión en sidebar
- Test de backend integrado
- Manejo de errores visual

## 🔐 Seguridad

- Variables de entorno para credenciales
- Validación de entrada
- CORS configurado
- Timeouts en requests

## 📈 Escalabilidad

- Backend serverless en IBM Cloud
- Frontend estático en Streamlit Cloud
- Separación de responsabilidades
- Cache de embeddings

## 🎯 Casos de Uso

1. **Preguntas sobre releases**: "¿Qué hay de nuevo en RelativityOne 2024.1?"
2. **Búsqueda de features**: "¿Cuándo se agregó la funcionalidad X?"
3. **Información técnica**: "¿Cuáles son los requisitos del sistema?"
4. **Contacto cuando no hay info**: Solicita datos automáticamente

## 📚 Documentación

- [Backend README](backend_ibm/README.md)
- [Frontend README](frontend_streamlit/README.md)
- [Configuración IBM Cloud](backend_ibm/README.md#despliegue-en-ibm-cloud)
- [Configuración Streamlit Cloud](frontend_streamlit/README.md#opción-1-streamlit-cloud-recomendado) 