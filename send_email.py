import os
import smtplib
import ssl
import json
import feedparser
import urllib.parse
from google import genai
import time
import hashlib
import base64
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser as date_parser
import email_template

# --- CONFIGURATION ---
api_key = os.environ.get("GOOGLE_API_KEY")
email_sender = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")
service_account_info = json.loads(os.environ.get("GCP_SERVICE_ACCOUNT"))
gemini_key = os.environ.get("GEMINI_API_KEY")

# ⚠️ PASTE YOUR SPREADSHEET ID HERE ⚠️
SPREADSHEET_ID = '1jaE61a613sqmxQnT_UncrbHzAsqYPqDwdIZGqoJ5Lc8'
RANGE_NAME = 'Sheet1!A:C'

# --- AI SETUP ---
if gemini_key:
    client = genai.Client(api_key=gemini_key)

# --- AI RATE LIMITING ---
AI_CALL_DELAY = 6.5  # 6.5 seconds between calls (gemini-2.0-flash-exp: 10 requests/min max)
ai_call_count = 0
MAX_AI_CALLS_PER_RUN = 50  # Reduced limit to stay well under quota

# --- HYBRID MAPPING (English Topic -> Chinese Search Term) ---
CHINESE_MAPPING = {
    # NEW 10-CATEGORY STRUCTURE
    # 🔋 Battery Technologies
    "Next-Gen Batteries": "固态电池 OR 钠离子电池 OR 下一代电池",
    "Advanced Materials": "硅负极 OR 锂金属负极 OR 磷酸铁锂 OR LMFP",
    "Energy Storage Systems": "储能电站 OR 工商业储能 OR 全钒液流电池",
    "Battery Safety & Performance": "电池 热失控 安全 OR 电池测试",

    # 🏛️ Policy & Markets
    "US Policy & Incentives": "IRA法案 电池 OR 通胀削减法案 电池 OR 美国 电池 补贴",
    "EU Regulations": "电池护照 欧盟 OR 欧盟电池法规 OR CBAM 电池",
    "China Industry & Trade": "电池 出口管制 商务部 OR 动力电池 产业政策",

    # ♻️ Supply Chain & Sustainability
    "Critical Minerals & Mining": "锂矿 开采 OR 关键矿产 电池 OR 钴矿 镍矿",
    "Manufacturing & Gigafactories": "动力电池 投产 OR 电池工厂 OR 电动汽车 供应链",
    "Recycling & Circular Economy": "动力电池回收 OR 电池循环利用 OR 黑粉",

    # LEGACY SUPPORT - Keep old categories for existing subscribers
    "Solid State Batteries": "固态电池",
    "Sodium-Ion": "钠离子电池",
    "Silicon Anode": "硅负极 电池",
    "LFP Battery": "磷酸铁锂 电池",
    "Lithium Metal Anode": "锂金属负极",
    "Vanadium Redox Flow": "全钒液流电池",
    "Inflation Reduction Act": "IRA法案 电池 OR 通胀削减法案 电池",
    "Battery Passport Regulation": "电池护照 欧盟",
    "China Battery Supply Chain & Policy": "电池 出口管制 商务部",
    "Critical Minerals & Mining": "锂矿 开采 OR 关键矿产 电池",
    "Geopolitics & Tariffs": "电池 关税 欧盟 OR 301条款 电池",
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

def generate_unsubscribe_token(email):
    """Create secure unsubscribe token"""
    secret_salt = os.environ.get("UNSUBSCRIBE_SALT", "default_salt_change_me")
    token = hashlib.sha256(f"{email}{secret_salt}".encode()).hexdigest()[:16]
    email_encoded = base64.urlsafe_b64encode(email.encode()).decode()
    return f"{email_encoded}.{token}"

def ai_summarize_article(title, snippet="", is_chinese=False):
    """
    Universal AI summarizer for all articles using Gemini 2.5

    Args:
        title: Article title
        snippet: Article snippet/description
        is_chinese: Whether article is in Chinese

    Returns: 1-sentence summary, empty string if no value to add, or original title if AI fails
    """
    global ai_call_count

    if not gemini_key:
        return ""

    # Skip AI if snippet is too short (likely won't add value)
    if not is_chinese and len(snippet.strip()) < 50:
        print(f"   ⏭️  Skipping AI (snippet too short): {len(snippet)} chars")
        return ""

    if ai_call_count >= MAX_AI_CALLS_PER_RUN:
        print(f"⚠️  AI call limit reached ({MAX_AI_CALLS_PER_RUN}).")
        return ""

    try:
        # Rate limiting delay
        if ai_call_count > 0:
            time.sleep(AI_CALL_DELAY)

        ai_call_count += 1

        if is_chinese:
            prompt = f"""
            Translate and summarize this Chinese battery industry news in ONE clear sentence.

            Title: {title}
            Snippet: {snippet}

            Instructions:
            - Start with "🇨🇳 China Update:"
            - Focus on WHO is doing WHAT and WHY it matters
            - Include specific details (numbers, locations, companies)
            - Make it informative, not just a translation

            Example: "🇨🇳 China Update: CATL is building a $2B sodium-ion battery plant in Sichuan to target the budget EV market with 160 Wh/kg cells by 2025"
            """
        else:
            prompt = f"""
            Analyze this battery industry article and provide a ONE-sentence insight.

            Title: {title}
            Snippet: {snippet}

            Instructions:
            - Extract KEY FACTS not in the title (numbers, specs, implications)
            - Focus on business impact or technical details
            - Be specific and informative
            - If the snippet adds NO new information beyond the title, respond with exactly: "SKIP"

            Good: "The plant will produce 50 GWh annually using LFP chemistry, targeting the commercial vehicle market with 2025 production start"
            Bad: "Company announces battery technology partnership" (too vague)
            """

        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt
        )
        summary = response.text.strip()

        # Skip if AI determines no value
        if summary == "SKIP" or "Details not available" in summary:
            print(f"   ⏭️  AI determined no additional value")
            return ""

        print(f"   🤖 AI Summary ({ai_call_count}/{MAX_AI_CALLS_PER_RUN}): {summary[:60]}...")
        return summary

    except Exception as e:
        error_str = str(e)
        # Check if it's a rate limit error
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            print(f"⚠️  Rate limit hit. Skipping remaining AI calls for this run.")
            # Set count to max to stop further API calls
            ai_call_count = MAX_AI_CALLS_PER_RUN
        else:
            print(f"⚠️  AI Error: {e}")
        return ""

def send_email():
    if not email_sender or not email_password:
        print("Error: Secrets not found.")
        return

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
            
            print(f"🔎 Scouting news for: {user_email}")

            # Use new email template
            email_body_html = email_template.get_email_header()

            news_found_count = 0
            topic_list = raw_topics.split("|")
            topics_with_articles = []  # Track which topics have articles for subject line

            # TRACKING SETS (Reset per user)
            seen_urls = set()
            seen_titles = set()

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
                topic_article_count = 0

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

                        # --- DUPLICATE CHECKER ---
                        clean_title = entry.title.split(" - ")[0].strip().lower()
                        if entry.link in seen_urls or clean_title in seen_titles:
                            continue

                        seen_urls.add(entry.link)
                        seen_titles.add(clean_title)
                        # -----------------------------------

                        # Add topic header if first article for this topic
                        if not topic_header_added:
                            # We'll add it after we know there are articles
                            topic_header_added = True

                        # PROCESS ARTICLE WITH AI
                        is_chinese = search["lang"] == "cn"
                        snippet = entry.summary if hasattr(entry, 'summary') else ""

                        # Get AI summary for ALL articles
                        ai_summary = ai_summarize_article(entry.title, snippet, is_chinese)

                        # Extract source from feed
                        source = "Unknown"
                        if hasattr(entry, 'source') and 'title' in entry.source:
                            source = entry.source['title']

                        # Add topic section header before first article
                        if topic_article_count == 0:
                            email_body_html += email_template.get_topic_section_header(topic)

                        # Add article card
                        email_body_html += email_template.get_article_card(
                            title=entry.title,
                            link=entry.link,
                            date=entry.published,
                            source=source,
                            summary=ai_summary,
                            is_chinese=is_chinese
                        )

                        news_found_count += 1
                        article_count += 1
                        topic_article_count += 1

                # Track topics that had articles for subject line
                if topic_article_count > 0:
                    topics_with_articles.append(topic)

            if news_found_count > 0:
                # Generate unsubscribe token and add footer
                unsubscribe_token = generate_unsubscribe_token(user_email)
                # Update with your actual Streamlit app URL
                unsubscribe_url = f"https://your-app.streamlit.app/?unsubscribe={unsubscribe_token}"
                email_body_html += email_template.get_email_footer(unsubscribe_url)

                # Enhanced subject line
                if len(topics_with_articles) == 1:
                    subject = f"⚡ Battery Scout: {topics_with_articles[0]} Updates"
                elif len(topics_with_articles) <= 3:
                    subject = f"⚡ Battery Scout: {', '.join(topics_with_articles[:2])} + More"
                else:
                    subject = f"⚡ Battery Scout: {news_found_count} Updates Across {len(topics_with_articles)} Topics"

                msg = MIMEMultipart()
                msg['From'] = f"Battery Scout <{email_sender}>"
                msg['To'] = user_email
                msg['Subject'] = subject
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