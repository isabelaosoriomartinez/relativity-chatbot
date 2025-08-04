"""
Flask backend for Relativity FAQ Chatbot.
Handles RESTful API routes for chatbot interactions and contact collection.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
import sys

# Add current directory to path for imports
sys.path.append('.')

from rag_ibm import RelativityRAGPipelineIBM
from sheets import GoogleSheetsLogger

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global variables for components
rag_pipeline = None
sheets_logger = None

def initialize_components():
    """Initialize RAG pipeline and Google Sheets logger."""
    global rag_pipeline, sheets_logger
    
    try:
        # Initialize RAG pipeline
        rag_pipeline = RelativityRAGPipelineIBM()
        
        # Check if vector store exists
        if not rag_pipeline.load_existing_vector_store():
            logger.warning("Vector store not found. Please run data ingestion first.")
            return False
        
        # Create QA chain
        rag_pipeline.create_qa_chain()
        
        # Initialize Google Sheets logger
        sheets_logger = GoogleSheetsLogger()
        if not sheets_logger.authenticate():
            logger.error("Failed to authenticate with Google Sheets")
            return False
        
        # Setup sheet
        sheets_logger.setup_sheet("Contact Submissions")
        
        logger.info("Components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "rag_pipeline": rag_pipeline is not None,
        "sheets_logger": sheets_logger is not None
    })

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handle chatbot questions."""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                "error": "Missing question in request body"
            }), 400
        
        question = data['question']
        
        if not rag_pipeline:
            return jsonify({
                "error": "RAG pipeline not initialized"
            }), 500
        
        # Query the RAG pipeline
        result = rag_pipeline.query(question)
        
        # Use the improved logic from RAG pipeline
        response = {
            "answer": result.get("answer", "No se pudo generar una respuesta."),
            "citations": result.get("citations", []),
            "has_sufficient_info": result.get("has_sufficient_info", False),
            "needs_contact": result.get("needs_contact", True)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in chatbot endpoint: {e}")
        return jsonify({
            "error": "Internal server error"
        }), 500

@app.route('/collect_contact', methods=['POST'])
def collect_contact():
    """Handle contact information collection."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "Missing request body"
            }), 400
        
        required_fields = ['name', 'email', 'organization', 'original_question']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
        
        name = data['name']
        email = data['email']
        organization = data['organization']
        original_question = data['original_question']
        
        if not sheets_logger:
            return jsonify({
                "error": "Google Sheets logger not initialized"
            }), 500
        
        # Validate contact information
        validation = sheets_logger.validate_contact_info(name, email, organization)
        
        if not validation["is_valid"]:
            return jsonify({
                "error": validation["error"],
                "success": False
            }), 400
        
        # Log contact information
        log_result = sheets_logger.log_contact(
            name=name,
            email=email,
            organization=organization,
            original_question=original_question,
            reason="insufficient_context"
        )
        
        if log_result["success"]:
            return jsonify({
                "message": "Contact information logged successfully. Our support team will reach out to you within 24-48 hours.",
                "success": True
            })
        else:
            return jsonify({
                "error": "Failed to log contact information",
                "success": False
            }), 500
        
    except Exception as e:
        logger.error(f"Error in collect_contact endpoint: {e}")
        return jsonify({
            "error": "Internal server error"
        }), 500

@app.route('/validate_contact', methods=['POST'])
def validate_contact():
    """Validate contact information format."""
    try:
        data = request.get_json()
        
        if not data or 'contact_text' not in data:
            return jsonify({
                "error": "Missing contact_text in request body"
            }), 400
        
        contact_text = data['contact_text']
        
        # Parse contact text (format: "Name | Email | Organization")
        parts = [part.strip() for part in contact_text.split('|')]
        
        if len(parts) != 3:
            return jsonify({
                "is_valid": False,
                "error": "Contact information must be in format: Name | Email | Organization"
            })
        
        name, email, organization = parts
        
        if not sheets_logger:
            return jsonify({
                "error": "Google Sheets logger not initialized"
            }), 500
        
        # Validate contact information
        validation = sheets_logger.validate_contact_info(name, email, organization)
        
        return jsonify({
            "is_valid": validation["is_valid"],
            "error": validation.get("error", ""),
            "parsed_data": {
                "name": name,
                "email": email,
                "organization": organization
            }
        })
        
    except Exception as e:
        logger.error(f"Error in validate_contact endpoint: {e}")
        return jsonify({
            "error": "Internal server error"
        }), 500

if __name__ == '__main__':
    # Initialize components
    if not initialize_components():
        logger.error("Failed to initialize components. Exiting.")
        sys.exit(1)
    
    # Get port from environment or use default
    port = int(os.getenv('CHATBOT_PORT', 5000))
    host = os.getenv('CHATBOT_HOST', '0.0.0.0')
    
    logger.info(f"Starting Flask server on {host}:{port}")
    app.run(host=host, port=port, debug=False) 