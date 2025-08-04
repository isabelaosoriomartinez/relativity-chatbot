# Google Sheets Setup Guide

This guide will help you set up Google Sheets integration for the Relativity FAQ chatbot.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Relativity FAQ Bot")
4. Click "Create"

## Step 2: Enable Google Sheets API

1. In your Google Cloud project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on "Google Sheets API" and then "Enable"

## Step 3: Create a Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the service account details:
   - Name: "relativity-faq-bot"
   - Description: "Service account for Relativity FAQ chatbot"
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 4: Generate Service Account Key

1. In the Credentials page, find your service account and click on it
2. Go to the "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" format
5. Click "Create"
6. The JSON file will download automatically

## Step 5: Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Name it "Relativity FAQ Contact Submissions"
4. Copy the Sheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
   - Copy the part between `/d/` and `/edit`

## Step 6: Share the Sheet

1. In your Google Sheet, click "Share" (top right)
2. Add the service account email (found in the JSON file under `client_email`)
3. Give it "Editor" permissions
4. Click "Send"

## Step 7: Configure the Application

1. Save the downloaded JSON file in your project directory
2. Update your `.env` file with:
   ```
   GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/service_account.json
   GOOGLE_SHEET_ID=your_sheet_id_here
   ```

## Step 8: Test the Integration

Run the test script to verify everything works:

```bash
python sheets.py
```

## Troubleshooting

### Common Issues:

1. **"Permission denied" error**
   - Make sure you shared the sheet with the service account email
   - Check that the service account has "Editor" permissions

2. **"Invalid credentials" error**
   - Verify the JSON file path is correct
   - Ensure the JSON file contains valid credentials

3. **"Sheet not found" error**
   - Verify the Sheet ID is correct
   - Make sure the sheet exists and is accessible

### Security Notes:

- Keep your service account JSON file secure
- Don't commit it to version control
- Consider using environment variables for production deployments

## Sheet Structure

The application will automatically create a worksheet called "Contact Submissions" with these columns:

| Column | Description |
|--------|-------------|
| Timestamp | When the contact was submitted |
| Name | User's name |
| Email | User's email address |
| Organization | User's organization |
| Original Question | The question that couldn't be answered |
| Reason for Escalation | Why the question was escalated |
| Status | Current status (New, In Progress, Resolved, etc.) | 