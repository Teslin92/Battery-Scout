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
api_key = os.environ.get("GOOGLE_API_KEY")
email_sender = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")
service_account_info = json.loads(os.environ.get("GCP_SERVICE_ACCOUNT"))

# ⚠️ PASTE YOUR SPREADSHEET ID HERE ⚠️
SPREADSHEET_ID = '1jaE61a613sqmxQnT_UncrbHzAsqYPqDwdIZGqoJ5Lc8' 
RANGE_NAME = 'Sheet1!A:C' 

def get_subscribers_from_sheet():
    creds = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])

def is_article_new(published_date_str):
    try:
        pub_date = date_parser.parse(published_date_str).replace(tzinfo=None)
        # Check if published in the last 24 hours
        if (datetime.utcnow() - pub_date) < timedelta(hours=24):
            return True
        return False
    except:
        return False

def send_email():
    if not email_sender or not email_password:
        print("Error: Secrets not found.")
        return

    try:
        rows = get_subscribers_from_sheet()
    except Exception as e:
        print(f"Failed to read Sheet: {e}")
        return

    subscribers = rows[1:] # Skip header
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)

        for row in subscribers:
            if len(row) < 2: continue
            user_email = row[0]
            raw_topics = row[1]
            
            if not user_email or "@" not in user_email: continue
            
            # --- CUSTOMIZED MESSAGE START ---
            # We build the message in a variable first
            email_body_html = """
            <h1 style='color: #2E86C1;'>🕵🏻‍♂️ The Battery Scout Brief</h1>
            <p>Here are the latest updates for your tracked topics from the last 24 hours:</p>
            <hr>
            """
            # --- CUSTOMIZED MESSAGE END ---
            
            news_found_count = 0
            topic_list = raw_topics.split("|")

            for topic in topic_list:
                if not topic: continue
                simple_topic = topic.replace('(', '').replace(')', '').split(' OR ')[0].replace('"', '')
                search_term = simple_topic if "battery" in simple_topic.lower() else f"{simple_topic} battery"

                safe_query = urllib.parse.quote(search_term)
                rss_url = f"https://news.google.com/rss/search?q={safe_query}+when:1d&hl=en-CA&gl=CA&ceid=CA:en"
                feed = feedparser.parse(rss_url)
                
                topic_header_added = False
                topic_article_count = 0

                for entry in feed.entries:
                    if topic_article_count >= 5: break 
                    if not is_article_new(entry.published): continue

                    if not topic_header_added:
                        email_body_html += f"<h3>🔋 {simple_topic.title()}</h3>"
                        topic_header_added = True
                    
                    email_body_html += f"<p>• <a href='{entry.link}'>{entry.title}</a> <span style='color: #888; font-size: 0.8em;'>({entry.published[:16]})</span></p>"
                    
                    news_found_count += 1
                    topic_article_count += 1

            if news_found_count > 0:
                # --- FOOTER ADDED HERE ---
                email_body_html += "<hr><p style='font-size: 12px; color: #666;'>Powered by Battery Scout Automation</p>"
                
                msg = MIMEMultipart()
                msg['From'] = email_sender
                msg['To'] = user_email
                msg['Subject'] = f"Battery Scout: {news_found_count} New Updates Today"
                
                # THIS WAS THE FIX:
                # We pass the variable 'email_body_html' directly, and tell it that it is 'html'
                msg.attach(MIMEText(email_body_html, 'html'))
                
                try:
                    smtp.sendmail(email_sender, user_email, msg.as_string())
                    print(f"✅ Sent email to {user_email}")
                except Exception as e:
                    print(f"❌ Failed to send: {e}")
            else:
                print(f"No news for {user_email}")

if __name__ == "__main__":
    send_email()
