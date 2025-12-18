import os
import smtplib
import ssl
import json
import feedparser
import urllib.parse
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser as date_parser

# --- CONFIGURATION ---
# Secrets from GitHub
api_key = os.environ.get("GOOGLE_API_KEY")
email_sender = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")
service_account_info = json.loads(os.environ.get("GCP_SERVICE_ACCOUNT"))

# Google Sheet Settings
SPREADSHEET_ID = '1jaE61a613sqmxQnT_UncrbHzAsqYPqDwdIZGqoJ5Lc8'  # <--- PASTE YOUR ID HERE AGAIN
RANGE_NAME = 'Sheet1!A:C' # Reading Columns A (Email) and B (Topics)

def get_subscribers_from_sheet():
    """Connects to Google Sheets and grabs the list"""
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])

def is_article_new(published_date_str):
    """Checks if the article was published in the last 24-48 hours"""
    try:
        # Parse the date string from the RSS feed
        pub_date = date_parser.parse(published_date_str)
        # Remove timezone info for comparison (make it "naive")
        pub_date = pub_date.replace(tzinfo=None)
        
        # Check if it is from the last 24 hours
        now = datetime.utcnow()
        if (now - pub_date) < timedelta(hours=24):
            return True
        return False
    except:
        # If we can't read the date, assume it's old to be safe
        return False

def send_email():
    if not email_sender or not email_password:
        print("Error: Secrets not found.")
        return

    print("🔌 Connecting to Google Sheets...")
    try:
        rows = get_subscribers_from_sheet()
    except Exception as e:
        print(f"Failed to read Sheet: {e}")
        return

    # Skip Header Row
    if not rows:
        print("Sheet is empty.")
        return
        
    subscribers = rows[1:]
    print(f"📋 Found {len(subscribers)} subscribers.")

    # Email Connection
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)

        for row in subscribers:
            # Safety check for empty rows
            if len(row) < 2: continue
            
            user_email = row[0]
            raw_topics = row[1] # "Lithium|Cobalt"
            
            if not user_email or "@" not in user_email: continue

            print(f"🔎 Scouting news for: {user_email}")

            # Prepare the Email Body
            email_body_html = "<h2>🔋 Daily Battery Updates</h2><hr>"
            news_found_count = 0
            
            # Split topics by the pipe symbol |
            topic_list = raw_topics.split("|")

            for topic in topic_list:
                if not topic: continue

                # CLEANUP LOGIC (From your original script)
                simple_topic = topic.replace('(', '').replace(')', '').split(' OR ')[0].replace('"', '')
                if "battery" not in simple_topic.lower() and "storage" not in simple_topic.lower():
                    search_term = f"{simple_topic} battery"
                else:
                    search_term = simple_topic

                # GOOGLE NEWS SEARCH
                safe_query = urllib.parse.quote(search_term)
                rss_url = f"https://news.google.com/rss/search?q={safe_query}+when:1d&hl=en-CA&gl=CA&ceid=CA:en"
                
                feed = feedparser.parse(rss_url)
                
                topic_header_added = False
                topic_article_count = 0

                for entry in feed.entries:
                    if topic_article_count >= 5: break # Max 5 articles per topic

                    # DATE CHECK (The Fix for "History.txt")
                    if not is_article_new(entry.published):
                        continue

                    if not topic_header_added:
                        email_body_html += f"<h3 style='color: #2E86C1;'>Topic: {simple_topic.title()}</h3>"
                        topic_header_added = True
                    
                    # Add Article to Email
                    email_body_html += f"<p><strong><a href='{entry.link}'>{entry.title}</a></strong><br>"
                    email_body_html += f"<span style='font-size: 12px; color: #666;'>{entry.published}</span></p>"
                    
                    news_found_count += 1
                    topic_article_count += 1

            # SEND THE EMAIL (Only if news was found)
            if news_found_count > 0:
                msg = MIMEMultipart()
                msg['From'] = email_sender
                msg['To'] = user_email
                msg['Subject'] = f"🕵🏻‍♂️ Battery Scout: {news_found_count} Battery News for You"
                msg.attach(MIMEText(email_body_html = "<h1>The Morning Battery Brief</h1><p>Here is what you missed in the last 24 hours:</p><hr>"))
                
                try:
                    smtp.sendmail(email_sender, user_email, msg.as_string())
                    print(f"✅ Sent email to {user_email} with {news_found_count} articles.")
                except Exception as e:
                    print(f"❌ Failed to send to {user_email}: {e}")
            else:
                print(f"💤 No new news for {user_email} today.")

if __name__ == "__main__":
    send_email()
