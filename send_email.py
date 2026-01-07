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

# --- MULTI-LANGUAGE MAPPING (English Topic -> Non-English Search Terms) ---
# Key battery industry countries: China, Germany, Japan, South Korea, Hungary, Sweden, France, Spain
MULTILANGUAGE_MAPPING = {
    # NEW 10-CATEGORY STRUCTURE
    # 🔋 Battery Technologies
    "Next-Gen Batteries": {
        "zh-CN": "固态电池 OR 钠离子电池 OR 下一代电池",
        "de": "Festkörperbatterie OR Natrium-Ionen-Batterie OR Feststoffbatterie",
        "ja": "全固体電池 OR ナトリウムイオン電池",
        "ko": "전고체 배터리 OR 나트륨 이온 배터리",
        "hu": "szilárdtest akkumulátor OR nátrium-ion akkumulátor",
        "sv": "faststatusbatteri OR natriumjonbatteri",
        "fr": "batterie solide OR batterie sodium-ion",
        "es": "batería de estado sólido OR batería de ión sodio"
    },
    "Advanced Materials": {
        "zh-CN": "硅负极 OR 锂金属负极 OR 磷酸铁锂 OR LMFP",
        "de": "Silizium-Anode OR Lithium-Metall-Anode OR LFP Batterie",
        "ja": "シリコン負極 OR リチウム金属負極 OR LFP電池",
        "ko": "실리콘 음극 OR 리튬 금속 음극",
        "hu": "szilícium anód OR lítium-fém anód",
        "sv": "kiselaluminium anod OR litiummetall anod",
        "fr": "anode silicium OR anode lithium métal OR LFP",
        "es": "ánodo de silicio OR ánodo de litio metálico"
    },
    "Energy Storage Systems": {
        "zh-CN": "储能电站 OR 工商业储能 OR 全钒液流电池",
        "de": "Energiespeicher OR Batteriespeicher OR Vanadium-Redox-Flow-Batterie",
        "ja": "蓄電システム OR バナジウムレドックスフロー電池",
        "ko": "에너지 저장 시스템 OR 바나듐 레독스 플로우 배터리",
        "hu": "energiatároló rendszer OR vanádium-redox áramlásos akkumulátor",
        "sv": "energilagring OR vanadium-redox-flödesbatteri",
        "fr": "stockage énergie OR batterie flux redox vanadium",
        "es": "almacenamiento energía OR batería de flujo redox de vanadio"
    },
    "Battery Safety & Performance": {
        "zh-CN": "电池 热失控 安全 OR 电池测试",
        "de": "Batterie Sicherheit OR thermisches Durchgehen OR Batterietest",
        "ja": "電池 安全性 OR 熱暴走",
        "ko": "배터리 안전 OR 열폭주",
        "hu": "akkumulátor biztonság OR hőrobbanás",
        "sv": "batterisäkerhet OR termisk rusning",
        "fr": "sécurité batterie OR emballement thermique",
        "es": "seguridad batería OR fuga térmica"
    },

    # 🏛️ Policy & Markets
    "US Policy & Incentives": {
        "zh-CN": "IRA法案 电池 OR 通胀削减法案 电池 OR 美国 电池 补贴",
        "de": "IRA Gesetz Batterie OR USA Batterieförderung",
        "ja": "IRA法 バッテリー OR 米国 電池 補助金",
        "ko": "IRA법 배터리 OR 미국 배터리 보조금",
        "hu": "IRA törvény akkumulátor OR USA akkumulátor támogatás",
        "sv": "IRA lag batteri OR USA batteristöd",
        "fr": "loi IRA batterie OR subventions batteries USA",
        "es": "ley IRA batería OR subsidios baterías EEUU"
    },
    "EU Regulations": {
        "zh-CN": "电池护照 欧盟 OR 欧盟电池法规 OR CBAM 电池",
        "de": "Batteriepass OR EU-Batterieverordnung OR CBAM Batterie",
        "ja": "バッテリーパスポート OR EU電池規制",
        "ko": "배터리 여권 OR EU 배터리 규정",
        "hu": "akkumulátor útlevél OR EU akkumulátor szabályozás",
        "sv": "batteripass OR EU batterireglering",
        "fr": "passeport batterie OR réglementation UE batteries",
        "es": "pasaporte batería OR regulación UE baterías"
    },
    "China Industry & Trade": {
        "zh-CN": "电池 出口管制 商务部 OR 动力电池 产业政策",
        "de": "China Batterie Exportkontrolle OR chinesische Batterieindustrie",
        "ja": "中国 電池 輸出規制 OR 中国 電池産業",
        "ko": "중국 배터리 수출 통제 OR 중국 배터리 산업",
        "hu": "Kína akkumulátor exportellenőrzés",
        "sv": "Kina batteri exportkontroll",
        "fr": "Chine contrôle export batterie OR industrie batterie chinoise",
        "es": "China control exportación batería OR industria batería china"
    },

    # ♻️ Supply Chain & Sustainability
    "Critical Minerals & Mining": {
        "zh-CN": "锂矿 开采 OR 关键矿产 电池 OR 钴矿 镍矿",
        "de": "Lithiumabbau OR kritische Mineralien Batterie OR Kobalt Nickel",
        "ja": "リチウム採掘 OR 重要鉱物 電池 OR コバルト ニッケル",
        "ko": "리튬 채굴 OR 핵심 광물 배터리 OR 코발트 니켈",
        "hu": "lítium bányászat OR kritikus ásványok akkumulátor",
        "sv": "litiumutvinning OR kritiska mineraler batteri",
        "fr": "extraction lithium OR minéraux critiques batterie OR cobalt nickel",
        "es": "extracción litio OR minerales críticos batería OR cobalto níquel"
    },
    "Manufacturing & Gigafactories": {
        "zh-CN": "动力电池 投产 OR 电池工厂 OR 电动汽车 供应链",
        "de": "Gigafactory OR Batteriefabrik OR Elektroauto Lieferkette",
        "ja": "ギガファクトリー OR 電池工場 OR 電気自動車 サプライチェーン",
        "ko": "기가팩토리 OR 배터리 공장 OR 전기차 공급망",
        "hu": "gigagyár OR akkumulátorgyár",
        "sv": "gigafabrik OR batterifabrik",
        "fr": "gigafactory OR usine batterie OR chaîne approvisionnement véhicule électrique",
        "es": "gigafábrica OR fábrica baterías OR cadena suministro vehículo eléctrico"
    },
    "Recycling & Circular Economy": {
        "zh-CN": "动力电池回收 OR 电池循环利用 OR 黑粉",
        "de": "Batterierecycling OR Kreislaufwirtschaft Batterie OR Schwarzmasse",
        "ja": "電池リサイクル OR 循環型経済 OR ブラックマス",
        "ko": "배터리 재활용 OR 순환경제 OR 블랙매스",
        "hu": "akkumulátor újrahasznosítás OR körforgásos gazdaság",
        "sv": "batteriåtervinning OR cirkulär ekonomi",
        "fr": "recyclage batterie OR économie circulaire OR masse noire",
        "es": "reciclaje batería OR economía circular OR masa negra"
    },

    # LEGACY SUPPORT - Keep old categories for existing subscribers
    "Solid State Batteries": {"zh-CN": "固态电池", "de": "Festkörperbatterie", "ja": "全固体電池"},
    "Sodium-Ion": {"zh-CN": "钠离子电池", "de": "Natrium-Ionen-Batterie", "ja": "ナトリウムイオン電池"},
    "Silicon Anode": {"zh-CN": "硅负极 电池", "de": "Silizium-Anode", "ja": "シリコン負極"},
    "LFP Battery": {"zh-CN": "磷酸铁锂 电池", "de": "LFP Batterie", "ja": "LFP電池"},
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

def ai_summarize_article(title, snippet="", is_translated=False, flag="", lang_code="en"):
    """
    Universal AI summarizer for all articles using Gemini 2.5

    Args:
        title: Article title
        snippet: Article snippet/description
        is_translated: Whether article is from non-English source
        flag: Flag emoji for the source country
        lang_code: Language code (e.g., "zh", "de", "ja")

    Returns: 1-sentence summary with flag prefix for translated content
    """
    global ai_call_count

    if not gemini_key:
        return ""

    # Skip AI if snippet is too short (likely won't add value) for English articles
    if not is_translated and len(snippet.strip()) < 50:
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

        if is_translated:
            # Language names for better prompts
            lang_names = {
                "zh": "Chinese",
                "de": "German",
                "ja": "Japanese",
                "ko": "Korean",
                "hu": "Hungarian",
                "sv": "Swedish",
                "fr": "French",
                "es": "Spanish"
            }
            lang_name = lang_names.get(lang_code, "foreign language")

            prompt = f"""
            Translate and summarize this {lang_name} battery industry news in ONE clear sentence.

            Title: {title}
            Snippet: {snippet}

            Instructions:
            - Start with "{flag} {lang_name} Update:"
            - Focus on WHO is doing WHAT and WHY it matters
            - Include specific details (numbers, locations, companies)
            - Make it informative, not just a translation

            Example: "{flag} {lang_name} Update: CATL is building a $2B sodium-ion battery plant in Sichuan to target the budget EV market with 160 Wh/kg cells by 2025"
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

    # Check if today is Monday (0 = Monday in Python's weekday())
    is_monday = datetime.now().weekday() == 0

    for row in subscribers:
        if len(row) < 2: continue
        user_email = row[0]
        raw_topics = row[1]
        # Get frequency preference (default to "Daily" for backward compatibility)
        frequency = row[2] if len(row) > 2 else "Daily"

        if not user_email or "@" not in user_email: continue

        # Skip weekly subscribers on non-Monday days
        if frequency == "Weekly" and not is_monday:
            print(f"⏭️  Skipping {user_email} (weekly subscriber, not Monday)")
            continue

        print(f"🔎 Scouting news for: {user_email} ({frequency})")

        # Use new email template
        email_body_html = email_template.get_email_header()

        news_found_count = 0
        topic_list = raw_topics.split("|")
        topics_with_articles = []  # Track which topics have articles for subject line

        # TRACKING SETS (Reset per user)
        seen_urls = set()
        seen_titles = set()

        # Language config: code, region, flag emoji
        LANGUAGES = [
            ("en", "US", "🇺🇸"),
            ("zh-CN", "CN", "🇨🇳"),
            ("de", "DE", "🇩🇪"),
            ("ja", "JP", "🇯🇵"),
            ("ko", "KR", "🇰🇷"),
            ("hu", "HU", "🇭🇺"),
            ("sv", "SE", "🇸🇪"),
            ("fr", "FR", "🇫🇷"),
            ("es", "ES", "🇪🇸")
        ]

        for topic in topic_list:
            if not topic: continue

            # 1. SETUP SEARCHES (English + Multiple Languages)
            searches = []

            simple_topic = topic.replace('(', '').replace(')', '').split(' OR ')[0].replace('"', '')

            # Always add English search
            eng_query = simple_topic if "battery" in simple_topic.lower() else f"{simple_topic} battery"
            searches.append({
                "lang": "en",
                "lang_code": "en-US",
                "term": simple_topic,
                "query": eng_query,
                "region": "US",
                "flag": "🇺🇸",
                "is_translated": False
            })

            # Add non-English searches if topic has translations
            if topic in MULTILANGUAGE_MAPPING and isinstance(MULTILANGUAGE_MAPPING[topic], dict):
                for lang_code, translated_query in MULTILANGUAGE_MAPPING[topic].items():
                    # Find matching language config
                    lang_info = next((l for l in LANGUAGES if l[0] == lang_code), None)
                    if lang_info:
                        searches.append({
                            "lang": lang_code.split('-')[0],  # "zh" from "zh-CN"
                            "lang_code": lang_code,
                            "term": simple_topic,
                            "query": translated_query,
                            "region": lang_info[1],
                            "flag": lang_info[2],
                            "is_translated": True
                        })

            topic_header_added = False
            topic_article_count = 0

            for search in searches:
                safe_query = urllib.parse.quote(search["query"])
                gl = search["region"]
                hl = search["lang_code"]

                rss_url = f"https://news.google.com/rss/search?q={safe_query}+when:1d&hl={hl}&gl={gl}&ceid={gl}:{hl}"
                feed = feedparser.parse(rss_url)

                article_count = 0

                for entry in feed.entries:
                    if article_count >= 2: break  # Max 2 articles per language (more languages now)
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
                    is_translated = search["is_translated"]
                    snippet = entry.summary if hasattr(entry, 'summary') else ""

                    # Get AI summary for translated articles (non-English)
                    ai_summary = ai_summarize_article(entry.title, snippet, is_translated, search["flag"], search["lang"])

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
                        is_chinese=is_translated  # True for any non-English article
                    )

                    news_found_count += 1
                    article_count += 1
                    topic_article_count += 1

            # Track topics that had articles for subject line
            if topic_article_count > 0:
                topics_with_articles.append(topic)

        print(f"📊 Total news found: {news_found_count}")

        if news_found_count > 0:
            print(f"✉️ Preparing email for {user_email} with {news_found_count} articles...")
            # Generate unsubscribe token and add footer
            unsubscribe_token = generate_unsubscribe_token(user_email)
            unsubscribe_url = f"https://battery-scout.streamlit.app/?unsubscribe={unsubscribe_token}"
            email_body_html += email_template.get_email_footer(unsubscribe_url)

            # Enhanced subject line
            frequency_prefix = "📬 Weekly Digest" if frequency == "Weekly" else "⚡ Daily Update"
            if len(topics_with_articles) == 1:
                subject = f"{frequency_prefix}: {topics_with_articles[0]}"
            elif len(topics_with_articles) <= 3:
                subject = f"{frequency_prefix}: {', '.join(topics_with_articles[:2])} + More"
            else:
                subject = f"{frequency_prefix}: {news_found_count} Updates Across {len(topics_with_articles)} Topics"

            msg = MIMEMultipart()
            msg['From'] = f"Battery Scout <{email_sender}>"
            msg['To'] = user_email
            msg['Subject'] = subject
            msg.attach(MIMEText(email_body_html, 'html'))

            # Create fresh SMTP connection for each email to avoid timeout
            print(f"📧 Attempting to send email to {user_email}...")
            try:
                context = ssl.create_default_context()
                print("  → Creating SMTP connection...")
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    print("  → Logging in...")
                    smtp.login(email_sender, email_password)
                    print("  → Sending message...")
                    smtp.sendmail(email_sender, user_email, msg.as_string())
                print(f"✅ Sent email to {user_email}")
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ Authentication failed: {e}")
                print(f"   Check EMAIL_ADDRESS and EMAIL_PASSWORD environment variables")
            except smtplib.SMTPException as e:
                print(f"❌ SMTP error: {e}")
                import traceback
                traceback.print_exc()
            except Exception as e:
                print(f"❌ Failed to send: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"No news for {user_email}")

if __name__ == "__main__":
    send_email()