import feedparser
import urllib.parse
import pandas as pd
import time
import smtplib
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURATION ---
YOUR_EMAIL = "zmeseldzija@gmail.com"  # <--- FILL THIS IN
YOUR_APP_PASSWORD = "mqhh hguf ivxf vgtr" # <--- FILL THIS IN
HISTORY_FILE = "history.txt"
SHEET_NAME = "Battery Subscribers" # <--- MATCH YOUR GOOGLE SHEET NAME

# --- GOOGLE SHEETS SETUP ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_subscribers_from_sheet():
    """Reads the Google Sheet and returns a DataFrame"""
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        
        # Get all values
        data = sheet.get_all_values()
        
        # Convert to DataFrame (assuming Row 1 is headers: "Email", "Topics")
        if not data:
            return pd.DataFrame()
            
        headers = data.pop(0) 
        df = pd.DataFrame(data, columns=headers)
        return df
    except Exception as e:
        print(f"❌ Error connecting to Google Sheets: {e}")
        return pd.DataFrame()

# --- HELPER FUNCTIONS ---
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_to_history(entry_id):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{entry_id}\n")

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = YOUR_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
        server.sendmail(YOUR_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# --- MAIN LOGIC ---
print("--- 🔋 STARTING BATTERY SCOUT (CLOUD DATA MODE) ---")

sent_papers = load_history()

# 1. READ FROM GOOGLE SHEETS INSTEAD OF CSV
print("   Connecting to Google Sheets...")
df = get_subscribers_from_sheet()

if df.empty:
    print("No subscribers found in the Sheet!")
    exit()
else:
    print(f"   Found {len(df)} subscribers.")

for index, row in df.iterrows():
    user_email = row['0'] if '0' in row else row.iloc[0] # Handle messy headers
    raw_topics = row['1'] if '1' in row else row.iloc[1]
    
    # Just in case the sheet headers are messy, we force column 0=Email, 1=Topics
    # Or if you named headers in the sheet, use row['Email']
    
    # Safety check
    if not user_email or "@" not in user_email:
        continue
        
    topics = raw_topics.split("|")
    
    print(f"\n📨 Processing: {user_email}")
    
    email_content = "<h2>🔋 Daily Battery Industry Updates</h2><hr>"
    new_items_count = 0
    
    for topic in topics:
        if not topic: continue
        
        # CLEANUP: '("silicon anode" OR "Si-anode")' -> 'silicon anode battery'
        simple_topic = topic.replace('(', '').replace(')', '').split(' OR ')[0].replace('"', '')
        if "battery" not in simple_topic.lower() and "storage" not in simple_topic.lower():
            search_term = f"{simple_topic} battery"
        else:
            search_term = simple_topic
            
        print(f"   🔎 Scouting Google News for: '{search_term}'...")
        safe_query = urllib.parse.quote(search_term)
        url = f"https://news.google.com/rss/search?q={safe_query}+when:7d&hl=en-CA&gl=CA&ceid=CA:en"
        
        feed = feedparser.parse(url)
        topic_count = 0
        topic_header_added = False
        
        for entry in feed.entries:
            if topic_count >= 5: break 
            news_id = entry.link
            
            if news_id in sent_papers:
                continue

            if simple_topic.lower() not in entry.title.lower() and simple_topic.lower() not in entry.summary.lower():
                continue

            if not topic_header_added:
                email_content += f"<h3 style='color: #2E86C1;'>Topic: {simple_topic.title()}</h3>"
                topic_header_added = True

            print(f"      📰 FOUND: {entry.title[:40]}...")
            
            email_content += f"<p><strong><a href='{entry.link}'>{entry.title}</a></strong><br>"
            email_content += f"<span style='font-size: 12px; color: #666;'>{entry.published}</span></p>"
            
            save_to_history(news_id)
            sent_papers.add(news_id)
            new_items_count += 1
            topic_count += 1
        
        time.sleep(1)

    if new_items_count > 0:
        print(f"   Found {new_items_count} updates. Sending email...")
        send_email(user_email, f"🔋 Battery Updates: {new_items_count} New Articles", email_content)
    else:
        print(f"   No new updates today.")

print("\n--- JOB COMPLETE ---")