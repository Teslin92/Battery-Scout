import os
import smtplib
import ssl
import json
import feedparser
import urllib.parse
import google.generativeai as genai
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
gemini_key = os.environ.get("GEMINI_API_KEY")

# --- TEST MODE ---
# Set TEST_MODE=true in GitHub Secrets to only send to TEST_EMAIL
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"
TEST_EMAIL = os.environ.get("TEST_EMAIL", email_sender)  # Defaults to your sender email

# ⚠️ PASTE YOUR SPREADSHEET ID HERE ⚠️
SPREADSHEET_ID = '1jaE61a613sqmxQnT_UncrbHzAsqYPqDwdIZGqoJ5Lc8' 
RANGE_NAME = 'Sheet1!A:C' 

# --- AI SETUP ---
if gemini_key:
    genai.configure(api_key=gemini_key)

# --- HYBRID MAPPING (English Topic -> Chinese Search Term) ---
CHINESE_MAPPING = {
    # 🧪 Tech & Chemistry
    "Solid State Batteries": "固态电池",
    "Sodium-Ion": "钠离子电池",
    "Silicon Anode": "硅负极 电池",
    "LFP Battery": "磷酸铁锂 电池",
    "Lithium Metal Anode": "锂金属负极",
    "Vanadium Redox Flow": "全钒液流电池",
    
    # 🏛️ Policy & Markets
    "Inflation Reduction Act": "IRA法案 电池 OR 通胀削减法案 电池",
    "Battery Passport Regulation": "电池护照 欧盟",
    "China Battery Supply Chain & Policy": "电池 出口管制 商务部",
    "Critical Minerals & Mining": "锂矿 开采 OR 关键矿产 电池",
    "Geopolitics & Tariffs": "电池 关税 欧盟 OR 301条款 电池",

    # ⚙️ Industry & Safety
    "Thermal Runaway & Safety": "电池 热失控 安全",
    "Gigafactory Construction": "动力电池 投产",
    "Grid Storage (BESS)": "储能电站 OR 工商业储能",
    "Electric Vehicle Supply Chain": "电动汽车 供应链",
    "Battery Recycling": "动力电池回收 OR 电池循环利用",
}

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
        if (datetime.utcnow() - pub_date) < timedelta(hours=24):
            return True
        return False
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Warning: Could not parse date '{published_date_str}': {e}")
        return False

def ai_summarize_chinese(title, snippet):
    """Uses Gemini to translate and summarize Chinese news"""
    if not gemini_key: return f"Translation unavailable: {title}"
    
    try:
        # UPDATED TO GEMINI 2.5
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Translate this Chinese battery news into English. 
        Title: {title}
        Snippet: {snippet}
        
        Task: Provide a 1-sentence summary of the core business or technical update. 
        Start with "🇨🇳 China Update:". Do not just translate the title.
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return f"🇨🇳 New Update (Translation Failed): {title}"

def send_email():
    if not email_sender or not email_password:
        print("Error: Secrets not found.")
        return

    # TEST MODE CHECK
    if TEST_MODE:
        print(f"⚠️  TEST MODE ENABLED - Only sending to: {TEST_EMAIL}")

    try:
        rows = get_subscribers_from_sheet()
    except Exception as e:
        print(f"Failed to read Sheet: {e}")
        return

    subscribers = rows[1:]
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)

        for row in subscribers:
            if len(row) < 2: continue
            user_email = row[0]
            raw_topics = row[1]

            if not user_email or "@" not in user_email: continue

            # TEST MODE: Skip all subscribers except the test email
            if TEST_MODE and user_email != TEST_EMAIL:
                print(f"⏭️  Skipping {user_email} (test mode)")
                continue

            print(f"🔎 Scouting news for: {user_email}")

            email_body_html = """
            <h1 style='color: #2E86C1;'>🕵🏻‍♂️ The Battery Scout Brief 🔋</h1>
            <p>Here are the latest updates for your tracked topics from the last 24 hours:</p>
            <hr>
            """
            
            news_found_count = 0
            topic_list = raw_topics.split("|")
            
            # TRACKING SETS (Reset per user)
            seen_urls = set() 
            seen_titles = set() # <--- NEW: Tracks titles to prevent syndication duplicates

            for topic in topic_list:
                if not topic: continue
                
                # 1. SETUP SEARCHES (English + Optional Chinese)
                searches = []
                
                # English Search
                simple_topic = topic.replace('(', '').replace(')', '').split(' OR ')[0].replace('"', '')
                eng_query = simple_topic if "battery" in simple_topic.lower() else f"{simple_topic} battery"
                searches.append({"lang": "en", "term": simple_topic, "query": eng_query, "region": "US"})
                
                # Chinese Search (Hybrid Mode)
                if topic in CHINESE_MAPPING:
                    cn_query = CHINESE_MAPPING[topic]
                    searches.append({"lang": "cn", "term": simple_topic, "query": cn_query, "region": "CN"})

                topic_header_added = False
                
                for search in searches:
                    safe_query = urllib.parse.quote(search["query"])
                    # Switch region based on language
                    gl = "CN" if search["lang"] == "cn" else "US"
                    hl = "zh-CN" if search["lang"] == "cn" else "en-US"
                    
                    rss_url = f"https://news.google.com/rss/search?q={safe_query}+when:1d&hl={hl}&gl={gl}&ceid={gl}:{hl}"
                    feed = feedparser.parse(rss_url)
                    
                    article_count = 0
                    
                    for entry in feed.entries:
                        if article_count >= 3: break # Max 3 articles per language
                        if not is_article_new(entry.published): continue

                        # --- DUPLICATE CHECKER (UPDATED) ---
                        # Clean title to remove source: "Battery News - CNN" -> "battery news"
                        clean_title = entry.title.split(" - ")[0].strip().lower()

                        if entry.link in seen_urls or clean_title in seen_titles: 
                            continue
                        
                        seen_urls.add(entry.link)
                        seen_titles.add(clean_title)
                        # -----------------------------------
                        
                        if not topic_header_added:
                            email_body_html += f"<h3>🔋 {simple_topic.title()}</h3>"
                            topic_header_added = True
                        
                        # PROCESS ARTICLE
                        display_title = entry.title
                        display_note = ""
                        
                        # If Chinese, call the AI
                        if search["lang"] == "cn":
                            print(f"   🤖 AI Analyzing: {entry.title[:15]}...")
                            ai_summary = ai_summarize_chinese(entry.title, entry.summary if hasattr(entry, 'summary') else "")
                            display_title = ai_summary # Replace title with AI summary
                            display_note = f"<br><a href='{entry.link}' style='font-size:0.8em'>[Original Chinese Source]</a>"
                        
                        email_body_html += f"<p>• <a href='{entry.link}'>{display_title}</a> <span style='color: #888; font-size: 0.8em;'>({entry.published[:16]})</span>{display_note}</p>"
                        
                        news_found_count += 1
                        article_count += 1

            if news_found_count > 0:
                email_body_html += "<hr><p style='font-size: 12px; color: #666;'>Powered by Battery Scout Automation</p>"
                msg = MIMEMultipart()
                msg['From'] = email_sender
                msg['To'] = user_email
                msg['Subject'] = f"Battery Scout: {news_found_count} New Updates Today"
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