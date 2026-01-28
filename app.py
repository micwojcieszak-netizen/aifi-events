import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random

# --- AIfi VISUALS ---
st.set_page_config(page_title="AIfi Events Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #007BFF !important; }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 20px; }
    .event-box { padding: 15px; border: 1px solid #eee; border-radius: 10px; margin-bottom: 10px; background: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE: SIMULATING 3-MONTH SCAN ---
def ai_scan_3_months():
    """Simulates scanning for Feb, March, April 2026"""
    teams = ["Arsenal", "Chelsea", "Man City", "Liverpool", "Spurs", "Newcastle", "Everton"]
    event_types = ["Premier League", "Champions League", "FA Cup", "Hospitality Event"]
    
    new_events = []
    # Generate 5 random events within the next 90 days
    for _ in range(5):
        days_ahead = random.randint(1, 90)
        date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        opponent = random.choice(teams)
        e_type = random.choice(event_types)
        
        new_events.append({
            "Date": date,
            "Event": f"AVFC vs {opponent}" if "Match" in e_type or "League" in e_type else f"{e_type} @ Villa Park",
            "Type": e_type
        })
    return pd.DataFrame(new_events).sort_values("Date")

# --- DATA PERSISTENCE ---
if 'master_log' not in st.session_state:
    st.session_state.master_log = pd.DataFrame(columns=["Date", "Event", "Type", "Status", "Reason", "Timestamp"])

if 'current_search' not in st.session_state:
    st.session_state.current_search = ai_scan_3_months()

# --- SIDEBAR ---
with st.sidebar:
    st.title("AIfi Intelligence")
    role = st.radio("Access Level:", ["Client", "Admin"])
    
    if role == "Admin":
        if st.text_input("Admin Password", type="password") != "aifi2026":
            st.stop()
    
    st.divider()
    # THE REFRESH BUTTON
    if st.button("🔄 Scrape Next 3 Months"):
        with st.spinner("AI Agent scanning Villa Park calendar (Feb-Apr 2026)..."):
            st.session_state.current_search = ai_scan_3_months()
            st.success("New data retrieved!")
            st.rerun()

# --- CLIENT VIEW ---
if role == "Client":
    st.title("⚽ AVFC Event Pipeline (Next 3 Months)")
    st.info("AI found these upcoming events. Select an action for each.")

    if st.session_state.current_search.empty:
        st.warning("No new events in the queue. Click 'Scrape' in the sidebar to find more.")
    
    for index, row in st.session_state.current_search.iterrows():
        with st.container():
            st.markdown(f"""<div class='event-box'>
                <b>{row['Event']}</b><br>
                <small>{row['Date']} | {row['Type']}</small>
            </div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 3, 1])
            status = c1.selectbox("Action", ["Pending", "Validate", "Cancelled"], key=f"s_{index}")
            
            reason = ""
            if status == "Cancelled":
                reason = c2.text_input("Reason?", key=f"r_{index}")
            
            if c3.button("Submit", key=f"b_{index}"):
                if status == "Pending":
                    st.error("Please select Validate or Cancelled")
                else:
                    new_entry = {
                        "Date": row["Date"], "Event": row["Event"], "Type": row["Type"],
                        "Status": status, "Reason": reason, "Timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.master_log = pd.concat([st.session_state.master_log, pd.DataFrame([new_entry])], ignore_index=True)
                    st.session_state.current_search = st.session_state.current_search.drop(index)
                    st.rerun()

# --- ADMIN VIEW ---
elif role == "Admin":
    st.title("🛠️ Admin Monitor")
    
    if st.session_state.master_log.empty:
        st.write("No client activity yet.")
    else:
        # Show validated vs cancelled
        st.write("### Processed Events History")
        st.dataframe(st.session_state.master_log, use_container_width=True)
        
        csv = st.session_state.master_log.to_csv(index=False).encode('utf-8')
        st.download_button("Download Admin Report", csv, "aifi_admin_report.csv")
