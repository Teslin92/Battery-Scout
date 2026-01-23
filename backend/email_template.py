"""
Email Template System for Battery Scout
Clean, minimal, mobile-responsive HTML email templates
"""

from datetime import datetime

def get_email_header(signup_url="https://battery-scout.streamlit.app"):
    """
    Generate email header with clean, minimal branding
    Returns: HTML string
    """
    today = datetime.now().strftime("%B %d, %Y")

    return f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: #ffffff;">
        <!-- Top Banner CTA -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #fafafa; padding: 12px 20px; border-bottom: 1px solid #eaeaea;">
            <tr>
                <td style="text-align: center;">
                    <a href="https://buymeacoffee.com/zmeseldzijv" style="display: inline-block; background: #FFDD00; color: #000; padding: 6px 14px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px; margin-right: 8px;">☕ Buy me a coffee</a>
                    <a href="{signup_url}" style="display: inline-block; background: #1a1a1a; color: #fff; padding: 6px 14px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px;">📧 Share</a>
                </td>
            </tr>
        </table>

        <!-- Header -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff; padding: 32px 20px 24px 20px;">
            <tr>
                <td style="text-align: center;">
                    <h1 style="color: #1a1a1a; margin: 0; font-size: 24px; font-weight: 600; letter-spacing: -0.5px;">
                        Battery Scout
                    </h1>
                    <p style="color: #888; margin: 6px 0 0 0; font-size: 13px; font-weight: 400;">
                        {today}
                    </p>
                </td>
            </tr>
        </table>

        <!-- Divider -->
        <div style="height: 1px; background: #eaeaea; margin: 0 20px;"></div>

        <!-- Intro -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff; padding: 20px 20px 8px 20px;">
            <tr>
                <td style="color: #555; font-size: 14px; line-height: 1.5;">
                    Your personalized battery industry updates:
                </td>
            </tr>
        </table>
    """


def get_topic_section_header(topic_name):
    """
    Generate topic section header - clean and minimal

    Args:
        topic_name: Name of the topic

    Returns: HTML string
    """
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background: #f5f5f5; padding: 14px 20px; margin-top: 24px; border-top: 2px solid #1a1a1a;">
        <tr>
            <td>
                <h2 style="color: #1a1a1a; margin: 0; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">
                    {topic_name}
                </h2>
            </td>
        </tr>
    </table>
    """


def get_article_card(title, link, date, source="Unknown", summary="", is_translated=False, flag=""):
    """
    Generate article card with light, minimal design

    Args:
        title: Article title
        link: Article URL
        date: Publication date
        source: News source (e.g., "Reuters", "Bloomberg")
        summary: AI-generated summary
        is_translated: Whether this is a non-English article
        flag: Country flag emoji for the article source

    Returns: HTML string
    """
    # Clean up date (take first 16 chars if longer)
    display_date = date[:16] if len(date) > 16 else date

    # Only show flag for translated articles
    flag_html = f'<span style="margin-right: 4px;">{flag}</span>' if flag else ''

    # Source link for translated articles
    translated_note = ""
    if is_translated:
        translated_note = f"""
        <span style="color: #999; margin-left: 8px;">
            · <a href='{link}' style="color: #999; font-size: 12px; text-decoration: none;">Original</a>
        </span>
        """

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff; padding: 12px 20px; border-bottom: 1px solid #f0f0f0;">
        <tr>
            <td>
                <!-- Title -->
                <div style="margin-bottom: 6px;">
                    {flag_html}<a href="{link}" style="color: #1a1a1a; font-size: 15px; font-weight: 500; text-decoration: none; line-height: 1.4;">
                        {title}
                    </a>
                </div>

                <!-- AI Summary -->
                {f'''
                <div style="color: #555; font-size: 14px; line-height: 1.5; margin: 8px 0;">
                    {summary}
                </div>
                ''' if summary else ''}

                <!-- Metadata -->
                <div style="margin-top: 6px;">
                    <span style="color: #999; font-size: 12px;">
                        {source} · {display_date}{translated_note}
                    </span>
                </div>
            </td>
        </tr>
    </table>
    """


def get_email_footer(unsubscribe_url="", signup_url="https://battery-scout.streamlit.app"):
    """
    Generate email footer - clean and minimal

    Args:
        unsubscribe_url: URL for unsubscribing
        signup_url: URL for new subscribers to sign up

    Returns: HTML string
    """
    # Build unsubscribe link if URL provided
    unsub_html = f'<a href="{unsubscribe_url}" style="color: #999; text-decoration: underline;">Unsubscribe</a><span style="margin: 0 6px; color: #ddd;">·</span>' if unsubscribe_url else ''

    return f"""
        <!-- Divider -->
        <div style="height: 1px; background: #eaeaea; margin: 32px 20px 0 20px;"></div>

        <!-- Bottom CTA - Prominent -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #fafafa; padding: 28px 20px;">
            <tr>
                <td style="text-align: center;">
                    <p style="color: #555; font-size: 14px; margin: 0 0 16px 0;">
                        Enjoying Battery Scout?
                    </p>
                    <a href="https://buymeacoffee.com/zmeseldzijv" style="display: inline-block; background: #FFDD00; color: #000; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 13px; margin-right: 10px;">☕ Buy me a coffee</a>
                    <a href="{signup_url}" style="display: inline-block; background: #1a1a1a; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 13px;">📧 Share</a>
                </td>
            </tr>
        </table>

        <!-- Footer -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff; padding: 20px; border-top: 1px solid #eaeaea;">
            <tr>
                <td style="text-align: center;">
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        AI-curated battery industry news
                    </p>
                    <p style="color: #999; font-size: 12px; margin: 12px 0 0 0;">
                        {unsub_html}© {datetime.now().year} Battery Scout
                    </p>
                </td>
            </tr>
        </table>
    </div>

    <!-- Mobile Responsive -->
    <style>
        @media only screen and (max-width: 600px) {{
            h1 {{ font-size: 22px !important; }}
            h2 {{ font-size: 12px !important; }}
        }}
    </style>
    """
