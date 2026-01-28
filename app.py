import streamlit as st
import pandas as pd
import time

# --- AIfi VISUAL CONFIGURATION ---
st.set_page_config(page_title="AIfi Events Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #007BFF !important; }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 20px; }
    .admin-box { border: 2px solid #007BFF; padding: 20px; border-radius: 10px; background-color: #f0f8ff; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if 'data' not in st.session_state:
    # Initial Mock Data
    st.session_state.data = pd.DataFrame([
        {"Date": "2026-02-01", "Event": "AVFC vs Brentford", "Type": "Premier League", "Valid": False},
        {"Date": "2026-02-14", "Event": "AVFC vs Liverpool", "Type": "Premier League", "Valid": False},
        {"Date": "2026-02-28", "Event": "Hospitality Tour Villa Park", "Type": "Other", "Valid": False},
    ])

# --- SIDEBAR & AUTHENTICATION ---
with st.sidebar:
    st.title("AIfi Access")
    role = st.radio("Select Role:", ["Client", "Admin"])
    
    if role == "Admin":
        password = st.text_input("Admin Password", type="password")
        if password != "aifi2026": # Temporary POC password
            st.warning("Please enter correct password to see Admin View")
            st.stop()
    
    st.divider()
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Aston_Villa_FC_crest_%282016%29.svg/1200px-Aston_Villa_FC_crest_%282016%29.svg.png", width=80)

# --- CLIENT VIEW ---
if role == "Client":
    st.title("⚽ Client Dashboard: AVFC")
    st.write("Please review the events below and check 'Valid' for those you approve.")

    for index, row in st.session_state.data.iterrows():
        c1, c2, c3, c4 = st.columns([2, 4, 2, 1])
        c1.write(row["Date"])
        c2.markdown(f"**{row['Event']}**")
        c3.caption(row["Type"])
        
        # This updates the master data frame
        is_valid = c4.checkbox("Valid", value=row["Valid"], key=f"client_{index}")
        st.session_state.data.at[index, "Valid"] = is_valid

    if st.button("Submit Validation"):
        st.success("Thank you! Your selections have been saved for the Admin.")
        st.balloons()

# --- ADMIN VIEW ---
elif role == "Admin":
    st.title("🛠️ Admin Control Panel")
    st.write("Overview of client activities and validated events.")

    # KPI Row
    total_events = len(st.session_state.data)
    validated_events = st.session_state.data["Valid"].sum()
    
    col_a, col_b = st.columns(2)
    col_a.metric("Total Events Found", total_events)
    col_b.metric("Validated by Client", validated_events)

    st.subheader("Full Data Log")
    
    # Custom styling for Admin Table
    def color_valid(val):
        color = '#d4edda' if val else '#f8d7da'
        return f'background-color: {color}'

    st.table(st.session_state.data.style.applymap(color_valid, subset=['Valid']))

    # Admin Export
    csv = st.session_state.data.to_csv(index=False).encode('utf-8')
    st.download_button("Download Final Report (CSV)", data=csv, file_name="admin_report.csv")
