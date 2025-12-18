import os
import smtplib
import ssl
import json
from email.message import EmailMessage
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 1. SETUP: Get secrets
api_key = os.environ.get("GOOGLE_API_KEY")
email_sender = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")
service_account_info = json.loads(os.environ.get("GCP_SERVICE_ACCOUNT"))

# SPREADSHEET SETUP
# Replace this with your actual Google Sheet ID (found in the URL of your sheet)
SPREADSHEET_ID = '1jaE61a613sqmxQnT_UncrbHzAsqYPqDwdIZGqoJ5Lc8' 
RANGE_NAME = 'Sheet1!A:B' # Adjust if your sheet name is different

def get_subscribers_from_sheet():
    """Connects to Google Sheets and grabs the list of emails"""
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    
    service = build('sheets', 'v4', credentials=creds)
    
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])
    return rows

def send_email():
    if not email_sender or not email_password:
        print("Error: Secrets not found.")
        return

    # Get fresh list from Google Sheets
    try:
        subscribers = get_subscribers_from_sheet()
    except Exception as e:
        print(f"Failed to read Google Sheet: {e}")
        return

    # Connect to Email Server
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        
        # Loop through the list from Google Sheets
        # We start at index 1 to skip the header row ("Email", "Date")
        for row in subscribers[1:]:
            if not row: continue # Skip empty rows
            
            email_receiver = row[0] # Assuming Email is Column A
            
            subject = "Daily Update"
            body = "Hello! This is a test sent using the live Google Sheet list."
            
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)
            
            try:
                smtp.sendmail(email_sender, email_receiver, em.as_string())
                print(f"Sent email to: {email_receiver}")
            except Exception as e:
                print(f"Failed to send to {email_receiver}: {e}")

if __name__ == "__main__":
    send_email()
