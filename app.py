import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

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

# --- MAIN APP LAYOUT ---
st.set_page_config(page_title="Battery Scout", page_icon="🔋")

st.title("🔋 Battery Scout")
st.write("Get a daily AI-curated email with the latest battery tech & policy news.")

with st.form("subscribe_form"):
    email = st.text_input("Your Email Address", placeholder="name@company.com")
    
    st.write("### Select Your Interests:")
    
    # --- CATEGORY 1: CHEMISTRY (The "Invisible Integration" Topics) ---
    # When users click these, we will eventually search English AND Chinese keywords
    with st.expander("🧪 Next-Gen Tech & Chemistry"):
        tech_choices = st.multiselect(
            "Select Tech Topics:",
            [
                "Solid State Batteries",
                "Sodium-Ion",
                "Silicon Anode",
                "LFP Battery",
                "Lithium Metal Anode",
                "Vanadium Redox Flow"
            ]
        )

    # --- CATEGORY 2: POLICY (With the New China Option) ---
    with st.expander("🏛️ Policy, Trade & Markets"):
        policy_choices = st.multiselect(
            "Select Policy Topics:",
            [
                "Inflation Reduction Act",
                "Battery Passport Regulation",
                "China Battery Supply Chain & Policy", # <--- NEW HYBRID ITEM
                "Critical Minerals & Mining",
                "Geopolitics & Tariffs",
            ]
        )

    # --- CATEGORY 3: INDUSTRIAL ---
    with st.expander("⚙️ Manufacturing & Safety"):
        industry_choices = st.multiselect(
            "Select Industry Topics:",
            [
                "Thermal Runaway & Safety",
                "Gigafactory Construction",
                "Grid Storage (BESS)",
                "Electric Vehicle Supply Chain"
                "Battery Recycling"
            ]
        )

    # Combine all choices into one list
    all_selected_topics = tech_choices + policy_choices + industry_choices

    submitted = st.form_submit_button("Subscribe for Free")

    if submitted:
        if email and "@" in email and all_selected_topics:
            with st.spinner("Saving your preferences..."):
                success = save_subscriber(email, all_selected_topics)
                if success:
                    st.success(f"✅ You're in! We'll start scouting news for: {', '.join(all_selected_topics)}")
        elif not email:
            st.warning("⚠️ Please enter your email.")
        elif not all_selected_topics:
            st.warning("⚠️ Please select at least one topic.")