"""
Email Template System for Battery Scout
Modern, mobile-responsive HTML email templates
"""

from datetime import datetime

def get_email_header():
    """
    Generate email header with branding and date
    Returns: HTML string
    """
    today = datetime.now().strftime("%B %d, %Y")

    return f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
        <!-- Header -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 20px; border-radius: 8px 8px 0 0;">
            <tr>
                <td style="text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 700;">
                        🕵🏻‍♂️ The Battery Scout Brief 🔋
                    </h1>
                    <p style="color: #f0f0f0; margin: 8px 0 0 0; font-size: 14px;">
                        Your daily dose of battery industry intelligence
                    </p>
                    <p style="color: #d0d0d0; margin: 8px 0 0 0; font-size: 12px;">
                        {today}
                    </p>
                </td>
            </tr>
        </table>

        <!-- Intro -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff; padding: 20px;">
            <tr>
                <td style="color: #4a5568; font-size: 14px; line-height: 1.6;">
                    Here are your personalized updates from the last 24 hours:
                </td>
            </tr>
        </table>

        <div style="height: 2px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);"></div>
    """


def get_topic_section_header(topic_name):
    """
    Generate topic section header

    Args:
        topic_name: Name of the topic

    Returns: HTML string
    """
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background: #f7fafc; padding: 16px 20px; margin-top: 20px;">
        <tr>
            <td>
                <h2 style="color: #2d3748; margin: 0; font-size: 18px; font-weight: 600;">
                    {topic_name}
                </h2>
            </td>
        </tr>
    </table>
    """


def get_article_card(title, link, date, source="Unknown", summary="", is_chinese=False):
    """
    Generate article card with modern design

    Args:
        title: Article title
        link: Article URL
        date: Publication date
        source: News source (e.g., "Reuters", "Bloomberg")
        summary: AI-generated summary
        is_chinese: Whether this is a Chinese article

    Returns: HTML string
    """
    # Clean up date (take first 16 chars if longer)
    display_date = date[:16] if len(date) > 16 else date

    # Source badge color based on type
    source_badge_color = "#667eea" if not is_chinese else "#e53e3e"
    source_label = f"🇨🇳 {source}" if is_chinese else source

    # Chinese article note
    chinese_note = ""
    if is_chinese:
        chinese_note = f"""
        <div style="margin-top: 8px;">
            <a href='{link}' style="color: #718096; font-size: 12px; text-decoration: none;">
                [View Original Chinese Source →]
            </a>
        </div>
        """

    return f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff; padding: 16px 20px; border-left: 4px solid #667eea; margin-top: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <tr>
            <td>
                <!-- Title -->
                <div style="margin-bottom: 8px;">
                    <a href="{link}" style="color: #2d3748; font-size: 16px; font-weight: 600; text-decoration: none; line-height: 1.4;">
                        {title}
                    </a>
                </div>

                <!-- AI Summary -->
                {f'''
                <div style="color: #4a5568; font-size: 14px; line-height: 1.5; margin-top: 8px; padding-left: 12px; border-left: 3px solid #667eea;">
                    {summary}
                </div>
                ''' if summary else ''}

                <!-- Metadata (Source & Date) -->
                <div style="margin-top: 8px;">
                    <span style="color: #a0aec0; font-size: 11px;">
                        {source_label if is_chinese else source} · {display_date}
                    </span>
                </div>

                <!-- Chinese Source Link -->
                {chinese_note}
            </td>
        </tr>
    </table>
    """


def get_email_footer(unsubscribe_url=""):
    """
    Generate email footer with branding and unsubscribe

    Args:
        unsubscribe_url: URL for unsubscribing

    Returns: HTML string
    """
    unsubscribe_link = ""
    if unsubscribe_url:
        unsubscribe_link = f"""
        <p style="color: #a0aec0; font-size: 11px; margin: 8px 0 0 0; text-align: center;">
            Don't want these emails? <a href="{unsubscribe_url}" style="color: #667eea; text-decoration: underline;">Unsubscribe</a>
        </p>
        """

    return f"""
        <!-- Footer -->
        <div style="height: 2px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); margin-top: 30px;"></div>

        <table width="100%" cellpadding="0" cellspacing="0" style="background: #f7fafc; padding: 30px 20px;">
            <tr>
                <td style="text-align: center;">
                    <p style="color: #4a5568; font-size: 14px; margin: 0 0 8px 0; font-weight: 600;">
                        ⚡ Powered by Battery Scout
                    </p>
                    <p style="color: #718096; font-size: 12px; margin: 0; line-height: 1.6;">
                        AI-curated battery industry news, delivered daily.<br>
                        Tracking technology, policy, and supply chain developments worldwide.
                    </p>

                    {unsubscribe_link}

                    <p style="color: #cbd5e0; font-size: 10px; margin: 16px 0 0 0;">
                        You're receiving this because you subscribed to Battery Scout updates.<br>
                        © {datetime.now().year} Battery Scout. All rights reserved.
                    </p>
                </td>
            </tr>
        </table>
    </div>

    <!-- Mobile Responsive CSS -->
    <style>
        @media only screen and (max-width: 600px) {{
            .article-card {{
                padding: 12px 16px !important;
            }}
            h1 {{
                font-size: 24px !important;
            }}
            h2 {{
                font-size: 16px !important;
            }}
        }}
    </style>
    """
