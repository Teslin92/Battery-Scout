"""
Battery Scout - News Scraping Service
Runs once daily to scrape news from all categories and languages,
generate AI summaries, and store in Supabase.
Separate from email sending for scalability.
"""

import os
import feedparser
import urllib.parse
from google import genai
import time
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser

from supabase_client import get_supabase_client, NEW_CATEGORIES

# --- CONFIGURATION ---
gemini_key = os.environ.get("GEMINI_API_KEY")

# --- AI SETUP ---
client = None
if gemini_key:
    client = genai.Client(api_key=gemini_key)

# --- AI RATE LIMITING ---
AI_CALL_DELAY = 6.5  # seconds between calls
ai_call_count = 0
MAX_AI_CALLS_PER_RUN = 150  # Enough for all categories


# --- SEARCH QUERIES ---
ENGLISH_SEARCH_QUERIES = {
    "Companies & Deals": "battery factory opening OR battery acquisition OR battery partnership OR battery product launch OR CATL OR BYD OR Tesla battery OR Northvolt",
    "Policy & Regulation": "EV tariff OR battery tariff OR EV subsidy policy OR battery regulation OR IRA battery credits OR EU battery law OR China EV tariff OR Canada EV tariff OR battery import duty OR electric vehicle trade policy",
    "Supply Chain": "lithium mining OR cobalt supply OR nickel battery OR battery materials shortage OR cathode production OR anode materials",
    "Lithium-ion & Solid-state": "solid-state battery OR lithium-ion breakthrough OR LFP battery OR NMC battery OR battery energy density",
    "Sodium-ion & Alternatives": "sodium-ion battery OR vanadium redox flow OR iron-air battery OR zinc battery OR alternative battery chemistry",
    "Recycling & Second-life": "battery recycling OR battery second life OR black mass OR battery circular economy OR EV battery reuse",
}

MULTILANGUAGE_MAPPING = {
    "Companies & Deals": {
        "zh-CN": "宁德时代 OR 比亚迪 OR 电池工厂 投产 OR 电池企业 收购 OR 动力电池 合作",
        "de": "Batteriefabrik Eröffnung OR Batterieunternehmen Übernahme OR Northvolt OR CATL",
        "ja": "電池工場 開設 OR バッテリー企業 買収 OR パナソニック 電池",
        "ko": "배터리 공장 OR 삼성SDI OR LG에너지솔루션 OR SK온 OR 배터리 인수",
        "hu": "akkumulátorgyár OR akkumulátor vállalat",
        "sv": "batterifabrik OR Northvolt OR batteriföretag",
        "fr": "usine batterie ouverture OR entreprise batterie acquisition",
        "es": "fábrica baterías OR empresa baterías adquisición"
    },
    "Policy & Regulation": {
        "zh-CN": "电池法规 OR 电池政策 OR 电池补贴 OR 电池关税 OR 新能源汽车政策 OR 电动汽车关税 OR 中国电动汽车出口",
        "de": "Batteriegesetz OR EU-Batterieverordnung OR Batterieförderung OR IRA Batterie OR EV Zoll OR Elektroauto Zoll",
        "ja": "電池規制 OR バッテリー政策 OR 電池補助金 OR EU電池規制 OR EV関税 OR 電気自動車関税",
        "ko": "배터리 규정 OR 배터리 정책 OR 배터리 보조금 OR IRA법 OR 전기차 관세",
        "hu": "akkumulátor szabályozás OR akkumulátor támogatás OR EV vám",
        "sv": "batterireglering OR batteripolicy OR EU batterireglering OR EV tull OR elbil tull",
        "fr": "réglementation batterie OR politique batterie OR subvention batterie OR tarif véhicule électrique OR droits douane VE",
        "es": "regulación batería OR política batería OR subvención batería OR arancel vehículo eléctrico"
    },
    "Supply Chain": {
        "zh-CN": "锂矿 开采 OR 钴矿 镍矿 OR 电池材料 OR 正极材料 OR 负极材料 OR 电池供应链",
        "de": "Lithiumabbau OR Kobalt Nickel Batterie OR Batteriematerialien OR Kathode Anode",
        "ja": "リチウム採掘 OR コバルト ニッケル 電池 OR 正極材料 OR 負極材料",
        "ko": "리튬 채굴 OR 코발트 니켈 배터리 OR 양극재 음극재 OR 배터리 공급망",
        "hu": "lítium bányászat OR akkumulátor anyagok",
        "sv": "litiumutvinning OR batterimaterial OR kobolt nickel",
        "fr": "extraction lithium OR matériaux batterie OR cobalt nickel",
        "es": "extracción litio OR materiales batería OR cobalto níquel"
    },
    "Lithium-ion & Solid-state": {
        "zh-CN": "固态电池 OR 锂离子电池 突破 OR 磷酸铁锂 OR 三元锂电池 OR 能量密度",
        "de": "Festkörperbatterie OR Lithium-Ionen Durchbruch OR LFP Batterie OR NMC",
        "ja": "全固体電池 OR リチウムイオン 技術突破 OR LFP OR NMC",
        "ko": "전고체 배터리 OR 리튬이온 돌파구 OR LFP OR NMC",
        "hu": "szilárdtest akkumulátor OR lítium-ion áttörés",
        "sv": "faststatusbatteri OR litiumjon genombrott",
        "fr": "batterie solide OR percée lithium-ion OR LFP",
        "es": "batería estado sólido OR avance litio-ion OR LFP"
    },
    "Sodium-ion & Alternatives": {
        "zh-CN": "钠离子电池 OR 全钒液流电池 OR 铁空气电池 OR 锌电池 OR 新型电池",
        "de": "Natrium-Ionen-Batterie OR Vanadium-Redox-Flow OR Eisen-Luft-Batterie",
        "ja": "ナトリウムイオン電池 OR バナジウムレドックスフロー OR 鉄空気電池",
        "ko": "나트륨이온 배터리 OR 바나듐 레독스 플로우 OR 철공기 배터리",
        "hu": "nátrium-ion akkumulátor OR vanádium redox",
        "sv": "natriumjonbatteri OR vanadium redox flöde",
        "fr": "batterie sodium-ion OR vanadium redox flow OR fer-air",
        "es": "batería sodio-ion OR vanadio redox flujo OR hierro-aire"
    },
    "Recycling & Second-life": {
        "zh-CN": "动力电池回收 OR 电池梯次利用 OR 黑粉回收 OR 电池循环经济",
        "de": "Batterierecycling OR Second-Life Batterie OR Schwarzmasse OR Kreislaufwirtschaft",
        "ja": "電池リサイクル OR セカンドライフ電池 OR ブラックマス OR 循環型経済",
        "ko": "배터리 재활용 OR 세컨드라이프 배터리 OR 블랙매스 OR 순환경제",
        "hu": "akkumulátor újrahasznosítás OR második élet akkumulátor",
        "sv": "batteriåtervinning OR second-life batteri OR cirkulär ekonomi",
        "fr": "recyclage batterie OR seconde vie batterie OR masse noire",
        "es": "reciclaje batería OR segunda vida batería OR masa negra"
    },
}

# Language/region configuration
ENGLISH_REGIONS = [
    ("US", "🇺🇸"),
    ("CA", "🇨🇦"),
    ("GB", "🇬🇧"),
    ("AU", "🇦🇺"),
]

NON_ENGLISH_LANGS = {
    "zh-CN": ("CN", "🇨🇳"),
    "de": ("DE", "🇩🇪"),
    "ja": ("JP", "🇯🇵"),
    "ko": ("KR", "🇰🇷"),
    "hu": ("HU", "🇭🇺"),
    "sv": ("SE", "🇸🇪"),
    "fr": ("FR", "🇫🇷"),
    "es": ("ES", "🇪🇸"),
}


def is_article_new(published_date_str: str) -> bool:
    """Check if article was published within last 24 hours."""
    try:
        pub_date = date_parser.parse(published_date_str).replace(tzinfo=None)
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        return (now_utc - pub_date) < timedelta(hours=24)
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Warning: Could not parse date '{published_date_str}': {e}")
        return False


def ai_summarize_article(
    title: str,
    snippet: str = "",
    is_translated: bool = False,
    lang_code: str = "en"
) -> tuple[str, bool]:
    """
    Generate AI summary for an article.
    Returns (summary, is_relevant) tuple.
    """
    global ai_call_count

    if not gemini_key or not client:
        return "", True

    if ai_call_count >= MAX_AI_CALLS_PER_RUN:
        print(f"⚠️  AI call limit reached ({MAX_AI_CALLS_PER_RUN}).")
        return "", True

    try:
        if ai_call_count > 0:
            time.sleep(AI_CALL_DELAY)

        ai_call_count += 1

        if is_translated:
            lang_names = {
                "zh": "Chinese", "de": "German", "ja": "Japanese",
                "ko": "Korean", "hu": "Hungarian", "sv": "Swedish",
                "fr": "French", "es": "Spanish"
            }
            lang_name = lang_names.get(lang_code, "foreign language")

            prompt = f"""
            Analyze this {lang_name} battery industry news article.

            Title: {title}
            Snippet: {snippet}

            FIRST, determine if this article is about news SPECIFIC to {lang_name}-speaking regions:
            - RELEVANT: News about companies, policies, factories, or events IN that region
            - NOT RELEVANT: Generic global industry news that just happens to be written in {lang_name}

            If NOT RELEVANT (just global news in another language), respond with exactly: "GENERIC"

            If RELEVANT, provide a ONE-sentence summary:
            - ALWAYS include the country/region in the summary (e.g., "German manufacturer", "South Korea's", "in France")
            - Include specific details: company names, $ amounts, GWh capacity, % tariff rates
            - Focus on the business impact for battery industry professionals
            - Write concisely but with enough context to understand the news
            """
        else:
            prompt = f"""
            Analyze this article for a BATTERY INDUSTRY PROFESSIONAL newsletter.

            Title: {title}
            Snippet: {snippet}

            This newsletter is for battery industry executives, engineers, and investors.
            They care about: manufacturing, technology breakthroughs, major deals, supply chain, and policy that directly affects battery production/sales.

            REJECT (respond "SKIP") if:
            - Consumer device news (phones, laptops, portable chargers)
            - Airline/travel battery policies (carry-on rules, flight bans)
            - Nuclear power or other non-battery energy (unless directly tied to battery storage)
            - Generic "EV sales up/down" without battery-specific angle
            - Market size projections ("market will reach $X billion")
            - Stock price movements without underlying business news
            - Product reviews or buying guides
            - Listicles or sponsored content

            ACCEPT only if directly relevant to battery industry professionals:
            - Battery factory news (openings, expansions, closures, investments)
            - Technology breakthroughs (new chemistries, energy density improvements, charging speeds)
            - Major deals (acquisitions, partnerships, supply agreements)
            - Raw materials & supply chain (lithium, cobalt, nickel mining/pricing)
            - Grid-scale energy storage projects
            - Battery recycling at industrial scale
            - Government incentives/regulations affecting battery manufacturers

            If REJECTED, respond with exactly: "SKIP"

            If ACCEPTED, provide a ONE-sentence summary:
            - ASSUME the reader is a well-informed industry professional who knows major political figures, CEOs, and policymakers by name (e.g., don't say "someone named Carney" - just say "Carney" or "Mark Carney")
            - ALWAYS include the country/region involved (e.g., "in Germany", "Canada announced", "Chinese manufacturer")
            - Include specifics: company names, $ amounts, GWh capacity, % tariff rates
            - Focus on the business impact for battery industry professionals
            - Write concisely but with enough context to understand the news without clicking
            - Write in a professional, direct tone - no hedging or unnecessary qualifiers
            """

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        summary = response.text.strip()

        # Check for rejection - catch exact matches and partial matches
        summary_upper = summary.upper()
        if (summary in ("GENERIC", "SKIP")
            or "GENERIC" in summary_upper
            or "SKIP" in summary_upper
            or "NOT RELEVANT" in summary_upper
            or "Details not available" in summary):
            print(f"   ⏭️  AI filtered article: {summary[:50]}")
            return "", False

        # Clean up prefixes
        for prefix in ["ACCEPT\n\n", "ACCEPT\n", "ACCEPT ", "ACCEPT:",
                       "RELEVANT: ", "RELEVANT\n\n", "RELEVANT\n"]:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()

        print(f"   🤖 AI Summary ({ai_call_count}/{MAX_AI_CALLS_PER_RUN}): {summary[:60]}...")
        return summary, True

    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            print(f"⚠️  Rate limit hit. Stopping AI calls.")
            ai_call_count = MAX_AI_CALLS_PER_RUN
        else:
            print(f"⚠️  AI Error: {e}")
        return "", True


def scrape_news():
    """
    Main scraping function. Runs once daily to collect all articles
    across all categories and languages, then stores them in Supabase.
    """
    global ai_call_count
    ai_call_count = 0

    print("🔍 Starting daily news scrape...")
    print(f"📂 Categories: {', '.join(NEW_CATEGORIES)}")

    supabase = get_supabase_client()

    # Track duplicates across all categories
    seen_urls = set()
    seen_titles = set()
    total_saved = 0

    for category in NEW_CATEGORIES:
        print(f"\n📰 Scraping: {category}")

        # Build search list for this category
        searches = []

        # English searches
        eng_query = ENGLISH_SEARCH_QUERIES.get(category, f"{category} battery")
        for region, flag in ENGLISH_REGIONS:
            searches.append({
                "lang": "en",
                "lang_code": f"en-{region}",
                "query": eng_query,
                "region": region,
                "flag": flag,
                "is_translated": False
            })

        # Non-English searches
        if category in MULTILANGUAGE_MAPPING:
            for lang_code, translated_query in MULTILANGUAGE_MAPPING[category].items():
                if lang_code in NON_ENGLISH_LANGS:
                    region, flag = NON_ENGLISH_LANGS[lang_code]
                    searches.append({
                        "lang": lang_code.split('-')[0],
                        "lang_code": lang_code,
                        "query": translated_query,
                        "region": region,
                        "flag": flag,
                        "is_translated": True
                    })

        category_count = 0

        for search in searches:
            safe_query = urllib.parse.quote(search["query"])
            gl = search["region"]
            hl = search["lang_code"]

            rss_url = f"https://news.google.com/rss/search?q={safe_query}+when:1d&hl={hl}&gl={gl}&ceid={gl}:{hl}"
            feed = feedparser.parse(rss_url)

            articles_from_source = 0

            for entry in feed.entries:
                if articles_from_source >= 3:  # Max 3 per language source
                    break

                if not is_article_new(entry.published):
                    continue

                # Duplicate check
                clean_title = entry.title.split(" - ")[0].strip().lower()
                if entry.link in seen_urls or clean_title in seen_titles:
                    continue

                seen_urls.add(entry.link)
                seen_titles.add(clean_title)

                # Get AI summary
                snippet = entry.summary if hasattr(entry, 'summary') else ""
                summary, is_relevant = ai_summarize_article(
                    entry.title, snippet,
                    search["is_translated"],
                    search["lang"]
                )

                if not is_relevant:
                    continue

                # Extract source name
                source = "Unknown"
                if hasattr(entry, 'source') and 'title' in entry.source:
                    source = entry.source['title']

                # Clean title
                display_title = entry.title
                if " - " in display_title:
                    display_title = display_title.rsplit(" - ", 1)[0]

                # Parse publish date
                try:
                    pub_date = date_parser.parse(entry.published)
                except Exception:
                    pub_date = datetime.now(timezone.utc)

                # Save to Supabase
                try:
                    supabase.table("articles").insert({
                        "title": display_title,
                        "url": entry.link,
                        "summary": summary,
                        "category": category,
                        "source_country": search["region"],
                        "source_name": source,
                        "publish_date": pub_date.isoformat(),
                        "flag": search["flag"],
                        "is_translated": search["is_translated"]
                    }).execute()

                    total_saved += 1
                    category_count += 1
                    articles_from_source += 1
                    print(f"   ✅ Saved: {display_title[:50]}...")

                except Exception as e:
                    if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                        pass  # Already exists
                    else:
                        print(f"   ⚠️  Error saving: {e}")

        print(f"   📊 {category}: {category_count} articles saved")

    print(f"\n✅ Scraping complete! Total articles saved: {total_saved}")
    print(f"🤖 AI calls used: {ai_call_count}/{MAX_AI_CALLS_PER_RUN}")


if __name__ == "__main__":
    scrape_news()
