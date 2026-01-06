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

def save_subscriber(email, topics):
    """Appends the user to the Google Sheet"""
    try:
        sheet = get_sheet()
        # Convert list ['Lithium', 'Cobalt'] -> string 'Lithium|Cobalt'
        topic_string = "|".join(topics)
        sheet.append_row([email, topic_string])
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
st.title("Battery Scout")
st.markdown("### Stay ahead of the battery industry with AI-curated daily news")
st.write("Get personalized updates on technology breakthroughs, policy changes, and supply chain developments delivered to your inbox.")

with st.form("subscribe_form"):
    email = st.text_input("Email Address", placeholder="your.email@company.com")

    st.write("### Choose Your Topics")
    st.caption("Select one or more areas you'd like to track")

    # Create three columns for organized layout
    col1, col2, col3 = st.columns(3)

    # Battery Technologies
    with col1:
        st.markdown("**Battery Technologies**")
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
        st.markdown("**Policy & Markets**")
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
        st.markdown("**Supply Chain & Sustainability**")
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
    submitted = st.form_submit_button("Subscribe for Free", type="primary", use_container_width=True)

    if submitted:
        if email and "@" in email and all_selected_topics:
            with st.spinner("Saving your preferences..."):
                success = save_subscriber(email, all_selected_topics)
                if success:
                    st.success(f"Success! You're subscribed to {len(all_selected_topics)} topic(s). Check your inbox tomorrow for your first update.")
        elif not email:
            st.warning("Please enter your email address.")
        elif not all_selected_topics:
            st.warning("Please select at least one topic.")

# --- FEATURES SECTION ---
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**AI-Powered Summaries**")
    st.write("Every article includes a concise AI-generated summary so you can quickly identify what matters most.")
with col2:
    st.markdown("**Global Coverage**")
    st.write("Track developments from the US, EU, and China with bilingual news aggregation and translation.")
with col3:
    st.markdown("**Zero Spam**")
    st.write("Personalized daily digest delivered to your inbox. Unsubscribe anytime with one click.")

# --- DONATION SECTION ---
st.divider()
st.subheader("Support Battery Scout")
st.write("Help keep this service free and ad-free by supporting our infrastructure and AI costs.")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Buy Me a Coffee"):
        st.info("Payment integration coming soon. Thank you for your interest!")
with col2:
    if st.button("One-Time Donation"):
        st.info("Payment integration coming soon. Thank you for your interest!")
with col3:
    if st.button("Become a Sponsor"):
        st.info("Sponsorship opportunities coming soon!")

# --- FOOTER ---
st.divider()
st.caption("Battery Scout aggregates and curates publicly available news from Google News RSS feeds. © 2026 Battery Scout. All rights reserved.")