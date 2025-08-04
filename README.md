# Relativity FAQ Chatbot - MVP

A conversational chatbot that answers questions about Relativity releases using IBM watsonx.ai models and Flask backend with Streamlit frontend.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements_ibm.txt

# Copy environment template
cp env_template.txt .env
# Edit .env with your credentials
```

### 2. Run Data Ingestion
```bash
python ingest.py
```

### 3. Start the Application
```bash
# Terminal 1 (Backend)
python app.py

# Terminal 2 (Frontend)
streamlit run streamlit_app.py
```

### 4. Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:5000

## 📁 Project Structure

```
├── app.py                 # Flask backend API
├── streamlit_app.py       # Streamlit frontend
├── rag_ibm.py            # RAG pipeline with IBM watsonx.ai
├── ingest.py             # Data ingestion
├── sheets.py             # Google Sheets integration
├── requirements_ibm.txt  # Dependencies
├── Dockerfile            # Container config
├── docker-compose.yml    # Multi-service setup
└── test_setup.py         # Testing utilities
```

## 🔧 Configuration

### Environment Variables
```env
# IBM Watsonx.ai
IBM_WATSONX_API_KEY=your_api_key
IBM_WATSONX_PROJECT_ID=your_project_id

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/credentials.json
GOOGLE_SHEET_ID=your_sheet_id

# Flask Configuration
CHATBOT_PORT=5000
CHATBOT_HOST=0.0.0.0

# Frontend Configuration
BACKEND_URL=http://127.0.0.1:5000
```

## 🧪 Testing

### Manual Testing
```powershell
# Test backend health
Invoke-RestMethod -Uri "http://127.0.0.1:5000/health" -Method GET

# Test chatbot
Invoke-RestMethod -Uri "http://127.0.0.1:5000/chatbot" -Method POST -ContentType "application/json" -Body '{"question":"What are the new features?"}'

# Test contact collection
Invoke-RestMethod -Uri "http://127.0.0.1:5000/collect_contact" -Method POST -ContentType "application/json" -Body '{"name":"Test User","email":"test@example.com","organization":"Test Corp","original_question":"Test question"}'
```

### Automated Testing
```bash
python test_setup.py
```

## 🐳 Docker Deployment
```bash
# Local development
docker-compose up

# Production (IBM Code Engine)
# Follow deploy_ibm_code_engine.md
```

## 📚 Documentation

- **deploy_ibm_code_engine.md**: Production deployment guide
- **setup_google_sheets.md**: Google Sheets setup

## 🎯 Features

- ✅ Conversational FAQ interface with Streamlit
- ✅ IBM watsonx.ai LLM integration
- ✅ Contact information collection
- ✅ Google Sheets logging
- ✅ Citation tracking
- ✅ Docker containerization
- ✅ Flask RESTful API
- ✅ Real-time chat interface
- ✅ Backend health monitoring 