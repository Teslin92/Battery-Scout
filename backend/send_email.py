"""
Battery Scout - Email Sending Service
Reads pre-scraped articles from Supabase and sends personalized emails.
No scraping or AI calls - just email assembly and delivery.
Run scrape_news.py first to populate articles.
"""

import os
import re
import smtplib
import ssl
import hashlib
import base64
import html
import time
import uuid
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

import email_template
from supabase_client import (
    get_supabase_client,
    get_active_subscribers,
    NEW_CATEGORIES,
    filter_articles_by_regions,
)


def normalize_title(title: str) -> str:
    """Normalize title for deduplication comparison."""
    # Lowercase, remove punctuation, extra spaces
    normalized = title.lower()
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    # Remove common filler words
    for word in ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'for', 'of', 'in', 'on', 'with']:
        normalized = re.sub(rf'\b{word}\b', '', normalized)
    return re.sub(r'\s+', ' ', normalized).strip()


def deduplicate_articles(articles: list) -> list:
    """
    Remove duplicate articles covering the same story.
    Keeps the first (most recent) article when duplicates found.
    """
    seen_normalized = set()
    unique_articles = []

    for article in articles:
        title = article.get("title", "")
        normalized = normalize_title(title)

        # Check if we've seen a very similar title
        is_duplicate = False
        for seen in seen_normalized:
            # If 70%+ of words match, consider it duplicate
            words1 = set(normalized.split())
            words2 = set(seen.split())
            if len(words1) > 0 and len(words2) > 0:
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                if overlap > 0.7:
                    is_duplicate = True
                    break

        if not is_duplicate:
            seen_normalized.add(normalized)
            unique_articles.append(article)

    return unique_articles

# --- CONFIGURATION ---
email_sender = os.environ.get("EMAIL_ADDRESS") or os.environ.get("GMAIL_USER")
email_password = os.environ.get("EMAIL_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD")


def generate_unsubscribe_token(email: str) -> str:
    """Create secure unsubscribe token."""
    secret_salt = os.environ.get("UNSUBSCRIBE_SALT")
    if not secret_salt:
        raise ValueError(
            "UNSUBSCRIBE_SALT environment variable is required. "
            "Set it to a random secret string (e.g., generate with: openssl rand -hex 32)"
        )
    token = hashlib.sha256(f"{email}{secret_salt}".encode()).hexdigest()[:16]
    email_encoded = base64.urlsafe_b64encode(email.encode()).decode()
    return f"{email_encoded}.{token}"


def get_recent_articles(hours: int = 24):
    """Fetch articles from Supabase that were created in the last N hours."""
    supabase = get_supabase_client()

    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    response = (
        supabase.table("articles")
        .select("*")
        .gte("created_at", cutoff_time.isoformat())
        .order("publish_date", desc=True)
        .execute()
    )

    return response.data


def generate_plain_text_email(topics_with_articles, articles_by_category, regions, unsubscribe_url, frontend_url):
    """Generate plain text version of email for better deliverability."""
    today = datetime.now().strftime("%B %d, %Y")
    
    text = f"""Battery Scout
{today}

Your personalized battery industry updates:

"""
    
    # Only include categories that have articles (same as HTML version)
    for category in topics_with_articles:
        category_articles = articles_by_category.get(category, [])
        # Filter by subscriber's region preferences (same as HTML version)
        category_articles = filter_articles_by_regions(category_articles, regions)
        # Deduplicate and limit to top 4 (same as HTML version)
        unique_articles = deduplicate_articles(category_articles)
        top_articles = unique_articles[:4]
        
        if not top_articles:
            continue
        
        text += f"\n{'=' * 60}\n{category.upper()}\n{'=' * 60}\n\n"
        
        for article in top_articles:
            title = article.get("title", "Untitled")
            url = article.get("url", "#")
            summary = article.get("summary", "")
            source = article.get("source_name", "Unknown")
            pub_date = article.get("publish_date", "")
            display_date = pub_date[:16] if len(pub_date) > 16 else pub_date
            
            text += f"{title}\n"
            if summary:
                text += f"{summary}\n"
            text += f"Source: {source} | Date: {display_date}\n"
            text += f"Read more: {url}\n\n"
    
    text += f"""
{'=' * 60}

Unsubscribe: {unsubscribe_url}
Visit us: {frontend_url}

© {datetime.now().year} Battery Scout
AI-curated battery industry news
"""
    
    return text


def send_email():
    """
    Main email sending function.
    Reads articles from Supabase and sends personalized emails to subscribers.
    """
    if not email_sender or not email_password:
        print("Error: Email credentials not found.")
        print("  Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables")
        return

    # Fetch all recent articles once
    print("📰 Fetching recent articles from database...")
    all_articles = get_recent_articles(hours=24)
    print(f"   Found {len(all_articles)} articles from last 24 hours")

    if not all_articles:
        print("⚠️  No articles found. Run scrape_news.py first!")
        return

    # Group articles by category
    articles_by_category = {}
    for article in all_articles:
        cat = article.get("category", "Companies & Deals")
        if cat not in articles_by_category:
            articles_by_category[cat] = []
        articles_by_category[cat].append(article)

    print(f"📂 Articles by category:")
    for cat, arts in articles_by_category.items():
        print(f"   - {cat}: {len(arts)} articles")

    # Fetch subscribers
    try:
        subscribers = get_active_subscribers()
        print(f"\n📋 Found {len(subscribers)} active subscribers")
    except Exception as e:
        print(f"❌ Failed to fetch subscribers: {e}")
        return

    if not subscribers:
        print("No active subscribers found.")
        return

    # Check if today is Monday (for weekly subscribers)
    is_monday = datetime.now().weekday() == 0

    for subscriber in subscribers:
        user_email = subscriber.get("email")
        categories = subscriber.get("categories", NEW_CATEGORIES)
        frequency = subscriber.get("frequency", "daily")
        regions = subscriber.get("regions", ["Global"])

        if not user_email or "@" not in user_email:
            continue

        # Skip weekly subscribers on non-Monday days
        if frequency == "weekly" and not is_monday:
            print(f"⏭️  Skipping {user_email} (weekly subscriber, not Monday)")
            continue

        print(f"\n✉️  Building email for: {user_email} ({frequency})")
        print(f"   Categories: {', '.join(categories)}")
        print(f"   Regions: {', '.join(regions)}")

        # Get frontend URL for email links
        frontend_url = os.environ.get("FRONTEND_URL", "https://battery-scout-launchpad.vercel.app")

        # Build email
        email_body_html = email_template.get_email_header(frontend_url)
        news_found_count = 0
        topics_with_articles = []

        for category in categories:
            category_articles = articles_by_category.get(category, [])

            # Filter by subscriber's region preferences
            category_articles = filter_articles_by_regions(category_articles, regions)

            if not category_articles:
                continue

            # Deduplicate and limit to top 4 articles per category
            unique_articles = deduplicate_articles(category_articles)
            top_articles = unique_articles[:4]

            email_body_html += email_template.get_topic_section_header(category)
            topics_with_articles.append(category)

            for article in top_articles:
                # Format date for display
                pub_date = article.get("publish_date", "")
                if pub_date:
                    display_date = pub_date[:16] if len(pub_date) > 16 else pub_date
                else:
                    display_date = ""

                # Only show flag for translated (non-English) articles
                is_translated = article.get("is_translated", False)
                flag = article.get("flag", "") if is_translated else ""

                # Escape HTML to prevent XSS attacks from malicious RSS content
                safe_title = html.escape(article.get("title", "Untitled"))
                safe_summary = html.escape(article.get("summary", ""))
                safe_source = html.escape(article.get("source_name", "Unknown"))
                
                email_body_html += email_template.get_article_card(
                    title=safe_title,
                    link=article.get("url", "#"),
                    date=display_date,
                    source=safe_source,
                    summary=safe_summary,
                    is_translated=is_translated,
                    flag=flag
                )
                news_found_count += 1

        print(f"   📊 Total articles: {news_found_count}")

        if news_found_count > 0:
            # Add footer with unsubscribe link
            unsubscribe_token = generate_unsubscribe_token(user_email)
            unsubscribe_url = f"{frontend_url}/unsubscribe?token={unsubscribe_token}"
            email_body_html += email_template.get_email_footer(unsubscribe_url, frontend_url)

            # Build subject line
            if len(topics_with_articles) == 1:
                subject = f"🔋 Battery Scout: {topics_with_articles[0]}"
            elif len(topics_with_articles) <= 3:
                subject = f"🔋 Battery Scout: {', '.join(topics_with_articles[:2])} + More"
            else:
                subject = f"🔋 Battery Scout: {news_found_count} Updates Across {len(topics_with_articles)} Topics"

            # Create email message
            msg = MIMEMultipart('alternative')
            
            # Set proper From header using formataddr for better compatibility
            msg['From'] = formataddr(("Battery Scout", email_sender))
            msg['To'] = user_email
            msg['Subject'] = subject
            msg['Reply-To'] = email_sender  # Important for deliverability
            msg['Message-ID'] = f"<{uuid.uuid4()}@battery-scout>"
            msg['Precedence'] = 'bulk'  # Indicates this is a newsletter
            msg['List-Id'] = '<battery-scout.battery-scout-launchpad.vercel.app>'  # Helps with filtering
            
            # Add List-Unsubscribe headers (RFC 2369) - CRITICAL for deliverability
            msg['List-Unsubscribe'] = f'<{unsubscribe_url}>'
            msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'  # One-click unsubscribe support
            
            # Generate plain text version for better deliverability
            plain_text_body = generate_plain_text_email(
                topics_with_articles, 
                articles_by_category,
                regions,
                unsubscribe_url,
                frontend_url
            )
            
            # Attach both plain text and HTML versions
            msg.attach(MIMEText(plain_text_body, 'plain'))
            msg.attach(MIMEText(email_body_html, 'html'))

            # Send email with rate limiting to avoid triggering spam filters
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, user_email, msg.as_string())
                print(f"   ✅ Sent!")
                
                # Rate limiting: Gmail allows ~100 emails/day for free accounts
                # Add small delay between sends to avoid triggering spam filters
                # For bulk sending, consider using a transactional email service
                time.sleep(1)  # 1 second delay between emails
                
            except smtplib.SMTPAuthenticationError as e:
                print(f"   ❌ Auth failed: {e}")
            except smtplib.SMTPRecipientsRefused as e:
                print(f"   ❌ Recipient refused: {e}")
            except smtplib.SMTPSenderRefused as e:
                print(f"   ❌ Sender refused: {e}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        else:
            print(f"   ⚠️  No articles match subscriber's categories")

    print("\n✅ Email sending complete!")


if __name__ == "__main__":
    send_email()
