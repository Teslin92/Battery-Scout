import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import hashlib
import base64

# --- CONFIGURATION ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# ⚠️ MAKE SURE THIS MATCHES YOUR GOOGLE SHEET NAME EXACTLY
SHEET_NAME = "Battery Subscribers"

# --- GOOGLE SHEETS CONNECTION ---
def get_sheet():
    """Connects to Google Sheets"""
    # Create a credentials object from the Streamlit secrets
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def save_subscriber(email, topics, frequency="Daily"):
    """Appends the user to the Google Sheet"""
    try:
        sheet = get_sheet()
        # Convert list ['Lithium', 'Cobalt'] -> string 'Lithium|Cobalt'
        topic_string = "|".join(topics)
        # Sheet structure: Email | Topics | Frequency
        sheet.append_row([email, topic_string, frequency])
        return True
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return False

def verify_unsubscribe_token(token_string):
    """Verify unsubscribe token and extract email"""
    try:
        email_encoded, token = token_string.split('.')
        email = base64.urlsafe_b64decode(email_encoded).decode()
        # Verify with same salt as send_email.py
        secret_salt = st.secrets.get("unsubscribe_salt", "default_salt_change_me")
        expected_token = hashlib.sha256(f"{email}{secret_salt}".encode()).hexdigest()[:16]
        if token == expected_token:
            return email
    except Exception:
        return None
    return None

def remove_subscriber(email):
    """Remove subscriber from Google Sheet"""
    try:
        sheet = get_sheet()
        cell = sheet.find(email)
        if cell:
            sheet.delete_rows(cell.row)
            return True
    except Exception as e:
        st.error(f"Error removing subscriber: {e}")
        return False
    return False

# --- MAIN APP LAYOUT ---
st.set_page_config(
    page_title="Battery Scout - Daily Battery Industry News",
    page_icon="⚡",
    layout="wide"
)

# --- UNSUBSCRIBE HANDLING ---
query_params = st.query_params
if "unsubscribe" in query_params:
    st.title("Battery Scout - Unsubscribe")
    token = query_params["unsubscribe"]
    email = verify_unsubscribe_token(token)

    if email:
        st.write(f"### Confirm Unsubscribe")
        st.write(f"Email: **{email}**")
        st.write("Are you sure you want to unsubscribe from Battery Scout daily updates?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Unsubscribe", type="primary"):
                if remove_subscriber(email):
                    st.success("You've been successfully unsubscribed. Sorry to see you go!")
                    st.write("You will no longer receive Battery Scout emails.")
                else:
                    st.error("Could not find your email in our system. You may already be unsubscribed.")
        with col2:
            if st.button("No, Keep Me Subscribed"):
                st.info("Great! You'll continue receiving daily battery industry updates.")
    else:
        st.error("Invalid unsubscribe link. Please contact support if you need help.")
    st.stop()

# --- NORMAL SUBSCRIPTION PAGE ---

# Custom CSS for purple gradient theme
st.markdown("""
<style>
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .hero-title {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 16px;
    }
    .hero-subtitle {
        font-size: 22px;
        margin-bottom: 20px;
        opacity: 0.95;
    }
    .trust-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">Your Global Battery Intelligence Service</div>
    <div class="hero-subtitle">AI-curated and translated global battery news delivered to your inbox</div>
</div>
""", unsafe_allow_html=True)

# How It Works Section
st.markdown("## How Battery Scout Works")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1️⃣ Choose Topics")
    st.write("Select from 10 curated categories covering tech, policy, and supply chain")
with col2:
    st.markdown("### 2️⃣ Set Frequency")
    st.write("Get updates daily or weekly—whatever fits your schedule")
with col3:
    st.markdown("### 3️⃣ Stay Informed")
    st.write("Receive AI-summarized articles from trusted sources worldwide")

st.divider()

# Sample Email Preview
st.markdown("## 📬 What You'll Receive")
st.markdown("*Here's a preview of what Battery Scout emails look like:*")

with st.expander("👁️ View Sample Email", expanded=False):
    st.markdown("**Subject Line:** ⚡ Daily Update: Next-Gen Batteries, US Policy & Incentives + More")
    st.divider()

    # Email header styled box
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px; color: white; text-align: center; margin-bottom: 20px;'>
        <h2 style='margin: 0; color: white;'>🕵🏻‍♂️ The Battery Scout Brief 🔋</h2>
        <p style='margin: 5px 0 0 0; opacity: 0.9;'>Your daily dose of battery industry intelligence</p>
        <p style='margin: 5px 0 0 0; font-size: 12px; opacity: 0.8;'>January 6, 2026</p>
    </div>
    """, unsafe_allow_html=True)

    # Topic section 1
    st.markdown("### Next-Gen Batteries")
    st.markdown("""
    **QuantumScape announces breakthrough in solid-state battery production**
    *QuantumScape achieved 95% yield in their pilot production line using a new ceramic separator process, targeting 10 GWh annual capacity by 2027 for automotive applications.*
    <small style='color: #888;'>Bloomberg · Jan 6, 2026</small>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("""
    **CATL unveils sodium-ion battery with 200 Wh/kg energy density**
    *🇨🇳 China Update: CATL's third-generation sodium-ion battery reaches 200 Wh/kg, targeting budget EVs and energy storage with commercial production starting Q3 2026 at their Ningde facility.*
    <small style='color: #888;'>Reuters · Jan 6, 2026</small>
    """, unsafe_allow_html=True)

    st.divider()

    # Topic section 2
    st.markdown("### US Policy & Incentives")
    st.markdown("""
    **DOE announces $2B in battery manufacturing grants**
    *The Department of Energy allocated $2 billion across 15 projects to build domestic battery manufacturing capacity, prioritizing LFP and solid-state technologies with expected job creation of 8,000 positions.*
    <small style='color: #888;'>U.S. Department of Energy · Jan 6, 2026</small>
    """, unsafe_allow_html=True)

    st.divider()

    st.info("📧 **New Here?** Know someone interested in battery news? Forward this email!")
    st.warning("☕ **Enjoying Battery Scout?** Support our free service with a coffee")

st.divider()

# Subscription Form
st.markdown("## 🚀 Get Started - It's Free!")

with st.form("subscribe_form"):
    # Email input prominently at top
    email = st.text_input("📧 Email Address", placeholder="your.email@company.com")

    # Email frequency selection
    frequency = st.radio(
        "⏰ How often would you like updates?",
        ["Daily", "Weekly"],
        horizontal=True,
        help="Daily: Get updates every day. Weekly: Get a digest every Monday."
    )

    # Topics in expander to reduce cognitive load
    with st.expander("📂 Choose Your Topics (Select 1 or more)", expanded=True):
        st.caption("Pick the areas you want to track. You can change these anytime.")

        # Create three columns for organized layout
        col1, col2, col3 = st.columns(3)

        # Battery Technologies
        with col1:
            st.markdown("**⚡ Battery Technologies**")
            tech_choices = st.multiselect(
                "Technology",
                [
                    "Next-Gen Batteries",
                    "Advanced Materials",
                    "Energy Storage Systems",
                    "Battery Safety & Performance"
                ],
                label_visibility="collapsed"
            )
            st.caption("Solid state, sodium-ion, anodes/cathodes, grid storage")

        # Policy & Markets
        with col2:
            st.markdown("**🏛️ Policy & Markets**")
            policy_choices = st.multiselect(
                "Policy",
                [
                    "US Policy & Incentives",
                    "EU Regulations",
                    "China Industry & Trade"
                ],
                label_visibility="collapsed"
            )
            st.caption("IRA, tax credits, regulations, trade policy")

        # Supply Chain & Sustainability
        with col3:
            st.markdown("**♻️ Supply Chain & Sustainability**")
            supply_choices = st.multiselect(
                "Supply Chain",
                [
                    "Critical Minerals & Mining",
                    "Manufacturing & Gigafactories",
                    "Recycling & Circular Economy"
                ],
                label_visibility="collapsed"
            )
            st.caption("Mining, manufacturing, recycling, circularity")

    # Combine all choices into one list
    all_selected_topics = tech_choices + policy_choices + supply_choices

    st.write("")  # Spacing
    submitted = st.form_submit_button("🚀 Start My Free Subscription", type="primary", use_container_width=True)

    if submitted:
        if email and "@" in email and all_selected_topics:
            with st.spinner("Saving your preferences..."):
                success = save_subscriber(email, all_selected_topics, frequency)
                if success:
                    if frequency == "Daily":
                        st.success(f"Success! You're subscribed to {len(all_selected_topics)} topic(s). Check your inbox tomorrow for your first daily update.")
                    else:
                        st.success(f"Success! You're subscribed to {len(all_selected_topics)} topic(s). Check your inbox next Monday for your first weekly digest.")
        elif not email:
            st.warning("Please enter your email address.")
        elif not all_selected_topics:
            st.warning("Please select at least one topic.")

# --- WHY BATTERY SCOUT SECTION ---
st.divider()
st.markdown("## Why Battery Scout?")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🤖 AI-Powered Summaries")
    st.write("Every article includes a concise AI-generated summary so you can quickly identify what matters most.")
with col2:
    st.markdown("### 🌍 Global Coverage")
    st.write("Track developments from the US, EU, and China with bilingual news aggregation and translation.")
with col3:
    st.markdown("### ⚡ Zero Spam")
    st.write("Personalized digest delivered to your inbox. Unsubscribe anytime with one click.")

# --- WHO SHOULD SUBSCRIBE ---
st.divider()
st.markdown("## 👥 Who Uses Battery Scout?")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**🔬 Researchers**")
    st.write("Stay current on breakthroughs")
with col2:
    st.markdown("**💼 Investors**")
    st.write("Track market trends")
with col3:
    st.markdown("**🏭 Engineers**")
    st.write("Monitor tech advances")
with col4:
    st.markdown("**📊 Analysts**")
    st.write("Follow policy changes")

# --- FOOTER ---
st.divider()

# Support section in footer (compact)
col1, col2 = st.columns([2, 1])
with col1:
    st.caption("Battery Scout aggregates and curates publicly available news from Google News RSS feeds.")
    st.caption("© 2026 Battery Scout. All rights reserved.")
with col2:
    st.markdown("**☕ Support Us**")
    st.markdown("[Buy Me a Coffee →](https://buymeacoffee.com/batteryscout)")
    st.caption("Help keep this free!")