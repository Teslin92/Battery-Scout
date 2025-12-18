import feedparser
import urllib.parse
import pandas as pd
import time
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURATION ---
YOUR_EMAIL = "ENTER_EMAIL_HERE"  # <--- FILL THIS IN
YOUR_APP_PASSWORD = "ENTER_PASSWORD_HERE" # <--- FILL THIS IN
HISTORY_FILE = "history.txt"

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
    msg.attach(MIMEText(body, 'html')) # Changed to HTML for clickable links

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
print("--- 🔋 STARTING BATTERY SCOUT (GOOGLE NEWS MODE) ---")

sent_papers = load_history()

try:
    df = pd.read_csv('subscribers.csv')
except FileNotFoundError:
    print("No subscribers found! Go to app.py and sign up.")
    exit()

for index, row in df.iterrows():
    user_email = row['Email']
    topics = row['Topics'].split("|")
    
    print(f"\n📨 Processing: {user_email}")
    
    # We build an HTML email now so it looks better
    email_content = "<h2>🔋 Daily Battery Industry Updates</h2><hr>"
    new_items_count = 0
    
    for topic in topics:
        # CLEANUP: Google News hates complex boolean like "OR". 
        # We simplify the search to the main keyword.
        # Example: '("silicon anode" OR "Si-anode")' -> 'silicon anode battery'
        
        # We strip the complex syntax to just get a solid search phrase
        simple_topic = topic.replace('(', '').replace(')', '').split(' OR ')[0].replace('"', '')
        
        # Add "battery" to ensure context if it's missing
        if "battery" not in simple_topic.lower() and "storage" not in simple_topic.lower():
            search_term = f"{simple_topic} battery"
        else:
            search_term = simple_topic
            
        print(f"   🔎 Scouting Google News for: '{search_term}'...")
        
        # ENCODE URL
        safe_query = urllib.parse.quote(search_term)
        
        # GOOGLE NEWS RSS URL
        # This targets "Science" and "Technology" sections specifically
        url = f"https://news.google.com/rss/search?q={safe_query}+when:7d&hl=en-CA&gl=CA&ceid=CA:en"
        
        feed = feedparser.parse(url)
        
        # Get top 5 results PER TOPIC (You can change this number)
        topic_count = 0
        topic_header_added = False
        
        for entry in feed.entries:
            if topic_count >= 5: break # Limit to 5 articles per topic
            
            # Create a unique ID from the link so we don't repeat news
            news_id = entry.link
            
            if news_id in sent_papers:
                continue

            # FILTER: Basic keyword check to ensure relevance
            # If we search for "Silicon", we want to make sure it's not "Silicon Valley Bank"
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