"""
Google Sheets integration for logging user contact information.
Handles authentication, validation, and data logging.
"""

import os
import re
import datetime
from typing import Dict, Any, Optional
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsLogger:
    """Handles logging contact information to Google Sheets."""
    
    def __init__(self, credentials_path=None, sheet_id=None):
        from dotenv import load_dotenv; load_dotenv()
        self.credentials_path = credentials_path or os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        self.sheet_id = sheet_id or os.getenv("GOOGLE_SHEET_ID")
        assert self.credentials_path and self.sheet_id, "Faltan credenciales/ID de hoja"
        
    def authenticate(self) -> bool:
        """Authenticate with Google Sheets API."""
        try:
            # Define the scope
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials from service account file
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )
            
            # Create gspread client
            self.client = gspread.authorize(credentials)
            
            # Open the spreadsheet
            self.sheet = self.client.open_by_key(self.sheet_id)
            
            logger.info("Successfully authenticated with Google Sheets")
            return True
            
        except GoogleAuthError as e:
            logger.error(f"Google authentication error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error authenticating with Google Sheets: {e}")
            return False
    
    def setup_sheet(self, worksheet_name: str = "Contact Submissions") -> bool:
        """Setup the worksheet with headers if it doesn't exist."""
        try:
            # Try to get existing worksheet
            try:
                worksheet = self.sheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                # Create new worksheet
                worksheet = self.sheet.add_worksheet(
                    title=worksheet_name,
                    rows=1000,
                    cols=10
                )
            
            # Check if headers exist
            headers = worksheet.row_values(1)
            expected_headers = [
                "Timestamp",
                "Name",
                "Email",
                "Organization", 
                "Original Question",
                "Reason for Escalation",
                "Status"
            ]
            
            if not headers or headers != expected_headers:
                # Set headers
                worksheet.update('A1:G1', [expected_headers])
                logger.info(f"Set up headers in worksheet: {worksheet_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up worksheet: {e}")
            return False
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        
        # Basic email validation regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_contact_info(self, name: str, email: str, organization: str) -> Dict[str, Any]:
        """Validate contact information and return validation result."""
        errors = []
        
        if not name or not name.strip():
            errors.append("Name is required")
        
        if not email or not email.strip():
            errors.append("Email is required")
        elif not self.validate_email(email.strip()):
            errors.append("Invalid email format")
        
        if not organization or not organization.strip():
            errors.append("Organization is required")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def log_contact(self, 
                   name: str, 
                   email: str, 
                   organization: str, 
                   original_question: str, 
                   reason: str = "insufficient_context",
                   status: str = "New") -> Dict[str, Any]:
        """Log contact information to Google Sheets."""
        
        if not self.client or not self.sheet:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        # Validate contact information
        validation = self.validate_contact_info(name, email, organization)
        if not validation["is_valid"]:
            return {
                "success": False, 
                "error": "Invalid contact information",
                "validation_errors": validation["errors"]
            }
        
        try:
            # Get the worksheet
            worksheet = self.sheet.worksheet("Contact Submissions")
            
            # Prepare row data
            timestamp = datetime.datetime.utcnow().isoformat()
            row_data = [
                timestamp,
                name.strip(),
                email.strip(),
                organization.strip(),
                original_question,
                reason,
                status
            ]
            
            # Append row to worksheet
            worksheet.append_row(row_data)
            
            logger.info(f"Successfully logged contact for {email}")
            
            return {
                "success": True,
                "timestamp": timestamp,
                "row_added": True
            }
            
        except Exception as e:
            logger.error(f"Error logging contact to Google Sheets: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_recent_submissions(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent contact submissions from the sheet."""
        try:
            if not self.client or not self.sheet:
                if not self.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            worksheet = self.sheet.worksheet("Contact Submissions")
            
            # Get all data
            all_data = worksheet.get_all_records()
            
            # Sort by timestamp (assuming first column is timestamp)
            sorted_data = sorted(
                all_data, 
                key=lambda x: x.get('Timestamp', ''), 
                reverse=True
            )
            
            # Return limited results
            recent_data = sorted_data[:limit]
            
            return {
                "success": True,
                "submissions": recent_data,
                "total_count": len(all_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting recent submissions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_submission_status(self, row_number: int, status: str) -> Dict[str, Any]:
        """Update the status of a submission."""
        try:
            if not self.client or not self.sheet:
                if not self.authenticate():
                    return {"success": False, "error": "Authentication failed"}
            
            worksheet = self.sheet.worksheet("Contact Submissions")
            
            # Update status in column G (7th column)
            worksheet.update(f'G{row_number}', status)
            
            return {"success": True, "status_updated": True}
            
        except Exception as e:
            logger.error(f"Error updating submission status: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def create_sheets_logger(credentials_path: Optional[str] = None, 
                        sheet_id: Optional[str] = None) -> GoogleSheetsLogger:
    """Convenience function to create Google Sheets logger."""
    
    # Get credentials path from environment or parameter
    creds_path = credentials_path or os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    if not creds_path:
        raise ValueError("Google Sheets credentials path not provided")
    
    # Get sheet ID from environment or parameter
    sheet_id = sheet_id or os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("Google Sheet ID not provided")
    
    logger = GoogleSheetsLogger(creds_path, sheet_id)
    
    # Test authentication and setup
    if not logger.authenticate():
        raise Exception("Failed to authenticate with Google Sheets")
    
    if not logger.setup_sheet():
        raise Exception("Failed to setup Google Sheet")
    
    return logger

if __name__ == "__main__":
    # Test the Google Sheets integration
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    try:
        logger = create_sheets_logger()
        
        # Test logging a contact
        result = logger.log_contact(
            name="Test User",
            email="test@example.com",
            organization="Test Corp",
            original_question="What are the new features?",
            reason="test_submission"
        )
        
        print(f"Log result: {result}")
        
        if result["success"]:
            # Get recent submissions
            submissions = logger.get_recent_submissions(5)
            print(f"Recent submissions: {submissions}")
        
    except Exception as e:
        print(f"Error: {e}") 