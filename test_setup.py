"""
Simplified test setup for Relativity FAQ Chatbot MVP.
Tests the core components: IBM watsonx.ai integration, Flask backend, and Google Sheets.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables."""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        "IBM_WATSONX_API_KEY",
        "IBM_WATSONX_PROJECT_ID",
        "GOOGLE_SHEETS_CREDENTIALS_PATH",
        "GOOGLE_SHEET_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_imports():
    """Test module imports."""
    print("\n🔍 Testing Module Imports...")
    
    try:
        import flask
        import gradio
        import requests
        import gspread
        from google.auth import default
        print("✅ Core dependencies imported successfully")
        
        # Test our custom modules
        from rag_ibm import RelativityRAGPipelineIBM
        from sheets import GoogleSheetsLogger
        print("✅ Custom modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_data_files():
    """Test if required data files exist."""
    print("\n🔍 Testing Data Files...")
    
    required_files = [
        "relativity_releases.json",
        "chroma_db"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing data files: {missing_files}")
        print("   Run data ingestion first: python ingest.py")
        return False
    
    print("✅ All required data files exist")
    return True

def test_rag_pipeline():
    """Test RAG pipeline initialization."""
    print("\n🔍 Testing RAG Pipeline...")
    
    try:
        from rag_ibm import RelativityRAGPipelineIBM
        
        # Initialize pipeline
        pipeline = RelativityRAGPipelineIBM()
        
        # Test vector store loading
        if pipeline.load_existing_vector_store():
            print("✅ Vector store loaded successfully")
            
            # Test QA chain creation
            pipeline.create_qa_chain()
            print("✅ QA chain created successfully")
            
            return True
        else:
            print("❌ Vector store not found")
            return False
            
    except Exception as e:
        print(f"❌ RAG pipeline error: {e}")
        return False

def test_google_sheets():
    """Test Google Sheets integration."""
    print("\n🔍 Testing Google Sheets Integration...")
    
    try:
        from sheets import GoogleSheetsLogger
        
        # Initialize logger
        logger = GoogleSheetsLogger()
        
        # Test authentication
        if logger.authenticate():
            print("✅ Google Sheets authentication successful")
            
            # Test sheet setup
            logger.setup_sheet("Contact Submissions")
            print("✅ Google Sheets setup successful")
            
            return True
        else:
            print("❌ Google Sheets authentication failed")
            return False
            
    except Exception as e:
        print(f"❌ Google Sheets error: {e}")
        return False

def test_flask_backend():
    """Test Flask backend basic functionality."""
    print("\n🔍 Testing Flask Backend...")
    
    try:
        from app import app
        
        # Test app creation
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Flask app created successfully")
                print("✅ Health endpoint accessible")
                return True
            else:
                print("❌ Health endpoint failed")
                return False
                
    except Exception as e:
        print(f"❌ Flask backend error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Relativity FAQ Chatbot - MVP Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Module Imports", test_imports),
        ("Data Files", test_data_files),
        ("RAG Pipeline", test_rag_pipeline),
        ("Google Sheets", test_google_sheets),
        ("Flask Backend", test_flask_backend)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your MVP is ready to run.")
        print("\n🚀 Next steps:")
        print("1. Start backend: python app.py")
        print("2. Start frontend: python frontend.py")
        print("3. Or use Docker: docker-compose up")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common fixes:")
        print("1. Set up environment variables in .env file")
        print("2. Install dependencies: pip install -r requirements_ibm.txt")
        print("3. Run data ingestion: python ingest.py")
        print("4. Set up Google Sheets credentials")

if __name__ == "__main__":
    main() 