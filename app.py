import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "Battery Subscribers" # <--- MAKE SURE THIS MATCHES YOUR GOOGLE SHEET NAME EXACTLY

def connect_to_sheet():
    """Connects to Google Sheets using the JSON key"""
    # Streamlit Cloud handles secrets differently than local
    # We check if we are local or in the cloud
    if "gcp_service_account" in st.secrets:
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    else:
        # Local mode (using the file on your computer)
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
    
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def save_subscriber(email, topics):
    """Saves a new subscriber to Google Sheets"""
    try:
        sheet = connect_to_sheet()
        topic_string = "|".join(topics)
        # Append the row: [Email, Topics]
        sheet.append_row([email, topic_string])
        return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return False

# ... (Keep the rest of your Page Setup and Form code exactly the same)

# --- PAGE SETUP ---
st.set_page_config(page_title="Battery Insider", page_icon="🔋", layout="wide")

st.title("🔋 Battery Insider")
st.write("### The latest research, curated for you.")
st.write("Select specific battery technologies to track. We scan academic repositories daily.")

with st.form("signup_form"):
    email = st.text_input("Enter your email address", placeholder="researcher@example.com")
    
    st.write("---") 
    st.write("### 🔬 Customize your Feed")
    
    # --- SECTION 1: LITHIUM-ION CHEMISTRY ---
    st.write("#### 1. Lithium-Ion Chemistry")
    c1, c2, c3 = st.columns(3)
    with c1:
        opt_si     = st.checkbox("Silicon Anodes")
        opt_limetal= st.checkbox("Lithium Metal Anodes")
    with c2:
        opt_nmc    = st.checkbox("High-Nickel NMC")
        opt_lfp    = st.checkbox("LFP & LMFP")
    with c3:
        opt_solid  = st.checkbox("Solid-State Electrolytes")
        opt_sulfur = st.checkbox("Lithium-Sulfur (Li-S)")

    st.write("---")

    # --- SECTION 2: BEYOND LITHIUM ---
    st.write("#### 2. Beyond Lithium & Flow Batteries")
    c4, c5, c6 = st.columns(3)
    with c4:
        opt_vanadium = st.checkbox("Vanadium Redox Flow (VRFB)")
        opt_flow     = st.checkbox("Organic Flow Batteries")
    with c5:
        opt_sodium   = st.checkbox("Sodium-Ion (Na-ion)")
        opt_zinc     = st.checkbox("Zinc-Ion / Zinc-Air")
    with c6:
        opt_supercap = st.checkbox("Supercapacitors")
        opt_grid     = st.checkbox("Long Duration Storage (LDES)")

    st.write("---")

    # --- SECTION 3: ENGINEERING & LIFECYCLE ---
    st.write("#### 3. Engineering & Manufacturing")
    c7, c8, c9 = st.columns(3)
    with c7:
        opt_dry    = st.checkbox("Dry Electrode Coating")
        opt_ctp    = st.checkbox("Cell-to-Pack (CTP)")
    with c8:
        opt_recycle= st.checkbox("Recycling & Black Mass")
        opt_mining = st.checkbox("Direct Lithium Extraction (DLE)")
    with c9:
        opt_energy = st.checkbox("Manufacturing Energy & LCA")
        opt_safety = st.checkbox("Thermal Runaway & Safety")

    st.write("---")
    
    submitted = st.form_submit_button("Subscribe for Updates", type="primary")

    if submitted:
        if email:
            selected_queries = []
            
            # --- THE SAFETY-PROOFED QUERIES ---
            # notice we never use just "LFP" or "NMC" alone anymore.
            
            # Li-Ion
            if opt_si:      selected_queries.append('("silicon anode" OR "Si-anode" OR "Si/C composite")')
            if opt_limetal: selected_queries.append('("lithium metal anode" OR "Li-metal battery")')
            if opt_nmc:     selected_queries.append('("NMC cathode" OR "NMC battery" OR "high-nickel cathode")')
            if opt_lfp:     selected_queries.append('("lithium iron phosphate" OR "LFP battery" OR "LFP cathode" OR "LMFP")')
            if opt_solid:   selected_queries.append('("solid state battery" OR "solid electrolyte" OR "sulfide electrolyte")')
            if opt_sulfur:  selected_queries.append('("lithium-sulfur" OR "Li-S battery")')

            # Beyond Li
            if opt_vanadium:selected_queries.append('("vanadium redox" OR "VRFB" OR "vanadium flow")')
            if opt_flow:    selected_queries.append('("organic flow battery" OR "redox flow battery")')
            if opt_sodium:  selected_queries.append('("sodium-ion" OR "Na-ion battery" OR "hard carbon anode")')
            if opt_zinc:    selected_queries.append('("zinc-ion" OR "Zn-ion" OR "zinc-air battery")')
            if opt_supercap:selected_queries.append('("supercapacitor" OR "ultracapacitor")')
            if opt_grid:    selected_queries.append('("long duration energy storage" OR "grid storage battery")')

            # Engineering
            if opt_dry:     selected_queries.append('("dry electrode" OR "solvent-free electrode" OR "dry coating battery")')
            if opt_ctp:     selected_queries.append('("cell-to-pack" OR "cell-to-chassis" OR "module-free battery")')
            if opt_recycle: selected_queries.append('("battery recycling" OR "black mass" OR "hydrometallurgy battery")')
            if opt_mining:  selected_queries.append('("direct lithium extraction" OR "lithium brine" OR "DLE lithium")')
            if opt_energy:  selected_queries.append('("life cycle assessment battery" OR "LCA battery" OR "manufacturing energy battery")')
            if opt_safety:  selected_queries.append('("thermal runaway" OR "battery safety" OR "battery gas venting")')

            if selected_queries:
                save_subscriber(email, selected_queries)
                st.success(f"✅ Saved! {email} is now tracking {len(selected_queries)} topics.")
            else:
                st.warning("⚠️ Please select at least one topic.")
        else:
            st.error("⚠️ Please enter a valid email address.")