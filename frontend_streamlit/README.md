# Relativity FAQ Chatbot - Streamlit Frontend

Frontend Streamlit para el chatbot de Relativity FAQ que se conecta a un backend IBM.

## 🚀 Despliegue

### Opción 1: Streamlit Cloud (Recomendado)

1. **Subir a GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit frontend"
   git push origin main
   ```

2. **Conectar con Streamlit Cloud**
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Conecta tu repositorio de GitHub
   - Configura la ruta del archivo: `frontend_streamlit/streamlit_app.py`

3. **Configurar variables de entorno**
   - En Streamlit Cloud, ve a Settings → Secrets
   - Agrega:
     ```toml
     API_BASE_URL = "https://your-backend-url.codeengine.appdomain.cloud"
     ```

### Opción 2: Local Development

1. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar backend URL**
   ```bash
   export API_BASE_URL=http://127.0.0.1:5000
   ```

3. **Ejecutar**
   ```bash
   streamlit run streamlit_app.py
   ```

## 🔧 Configuración

### Variables de Entorno

- `API_BASE_URL`: URL del backend IBM (default: http://127.0.0.1:5000)

### Funcionalidades

- 💬 Chat interactivo con historial
- 📚 Citas y fuentes automáticas
- 📝 Formulario de contacto cuando es necesario
- 🔧 Configuración de backend desde la UI
- 🧪 Test de conectividad con el backend

## 🎨 Personalización

El frontend incluye CSS personalizado para:
- Mensajes de chat estilizados
- Citas con formato
- Formularios de contacto
- Indicadores de estado

## 🔗 Conectar con Backend

El frontend se conecta automáticamente al backend configurado en `API_BASE_URL`.

Endpoints utilizados:
- `GET /health`: Health check
- `POST /chatbot`: Procesar preguntas
- `POST /validate_contact`: Validar contacto
- `POST /collect_contact`: Registrar contacto

## 📱 Responsive Design

La aplicación está optimizada para:
- Desktop (layout wide)
- Tablet (columnas adaptativas)
- Mobile (formularios apilados) 