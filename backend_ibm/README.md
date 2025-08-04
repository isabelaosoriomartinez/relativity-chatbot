# Relativity FAQ Chatbot - IBM Backend

Backend API para el chatbot de Relativity FAQ usando IBM Watsonx.ai.

## 🚀 Despliegue en IBM Cloud

### Opción 1: IBM Code Engine (Recomendado)

1. **Instalar IBM Cloud CLI**
   ```bash
   curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
   ibmcloud login
   ```

2. **Crear proyecto y aplicación**
   ```bash
   ibmcloud ce project create --name relativity-chatbot
   ibmcloud ce project select --name relativity-chatbot
   ibmcloud ce app create --name relativity-backend --image docker.io/library/python:3.11-slim
   ```

3. **Configurar variables de entorno**
   ```bash
   ibmcloud ce app update --name relativity-backend \
     --env IBM_WATSONX_API_KEY=your_api_key \
     --env IBM_WATSONX_PROJECT_ID=your_project_id \
     --env GOOGLE_SHEETS_CREDENTIALS=your_credentials_json
   ```

4. **Desplegar**
   ```bash
   ibmcloud ce app deploy --name relativity-backend --source .
   ```

### Opción 2: Docker Local

1. **Construir imagen**
   ```bash
   docker build -t relativity-backend .
   ```

2. **Ejecutar contenedor**
   ```bash
   docker run -p 5000:5000 \
     -e IBM_WATSONX_API_KEY=your_api_key \
     -e IBM_WATSONX_PROJECT_ID=your_project_id \
     -e GOOGLE_SHEETS_CREDENTIALS=your_credentials_json \
     relativity-backend
   ```

## 🔧 Configuración

### Variables de Entorno

- `IBM_WATSONX_API_KEY`: API Key de IBM Watsonx.ai
- `IBM_WATSONX_PROJECT_ID`: Project ID de IBM Watsonx.ai
- `GOOGLE_SHEETS_CREDENTIALS`: JSON de credenciales de Google Sheets
- `CHATBOT_HOST`: Host del servidor (default: 0.0.0.0)
- `CHATBOT_PORT`: Puerto del servidor (default: 5000)

### Endpoints

- `GET /health`: Health check
- `POST /chatbot`: Procesar pregunta del chatbot
- `POST /validate_contact`: Validar información de contacto
- `POST /collect_contact`: Registrar información de contacto

## 📊 Monitoreo

- Health check: `GET /health`
- Logs: `ibmcloud ce app logs --name relativity-backend`

## 🔗 Conectar con Frontend

El frontend Streamlit debe configurar la variable `API_BASE_URL` para apuntar a la URL del backend desplegado.

Ejemplo:
```bash
export API_BASE_URL=https://relativity-backend.us-south.codeengine.appdomain.cloud
streamlit run ../frontend_streamlit/streamlit_app.py
``` 