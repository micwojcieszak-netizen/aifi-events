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
    .event-box { 
        padding: 15px; 
        border: 1px solid #e1e4e8; 
        border-left: 5px solid #007BFF;
        border-radius: 10px; 
        margin-bottom: 15px; 
        background: #fcfcfc; 
    }
    .time-badge {
        background-color: #e7f3ff;
        color: #007BFF;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE: SIMULATING 3-MONTH SCAN WITH TIME ---
def ai_scan_3_months():
    teams = ["Arsenal", "Chelsea", "Man City", "Liverpool", "Spurs", "Newcastle", "Everton"]
    event_types = ["Premier League", "Champions League", "FA Cup", "Hospitality Event"]
    times = ["12:30", "15:00", "17:30", "20:00", "20:45"]
    
    new_events = []
    for _ in range(5):
        days_ahead = random.randint(1, 90)
        date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        event_time = random.choice(times)
        opponent = random.choice(teams)
        e_type = random.choice(event_types)
        
        new_events.append({
            "Date": date,
            "Time": event_time,
            "Event": f"AVFC vs {opponent}" if "Match" in e_type or "League" in e_type else f"{e_type} @ Villa Park",
            "Type": e_type
        })
    return pd.DataFrame(new_events).sort_values(["Date", "Time"])

# --- DATA PERSISTENCE ---
if 'master_log' not in st.session_state:
    st.session_state.master_log = pd.DataFrame(columns=["Date", "Time", "Event", "Type", "Status", "Reason"])

if 'current_search' not in st.session_state:
    st.session_state.current_search = ai_scan_3_months()

# --- SIDEBAR ---
with st.sidebar:
    st.title("AIfi Control")
    role = st.radio("Access Level:", ["Client", "Admin"])
    
    if role == "Admin":
        if st.text_input("Admin Password", type="password") != "aifi2026":
            st.stop()
    
    st.divider()
    if st.button("🔄 Scrape Next 3 Months"):
        with st.spinner("AI Agent scanning Villa Park schedule..."):
            st.session_state.current_search = ai_scan_3_months()
            st.success("Refreshed with new times!")
            st.rerun()

# --- CLIENT VIEW ---
if role == "Client":
    st.title("⚽ AVFC Event Pipeline")
    st.info("Showing events for Feb - April 2026. Please validate.")

    if st.session_state.current_search.empty:
        st.warning("Queue is empty. Use 'Scrape' in sidebar.")
    
    for index, row in st.session_state.current_search.iterrows():
        with st.container():
            st.markdown(f"""
                <div class='event-box'>
                    <span class='time-badge'>🕒 {row['Time']}</span><br>
                    <div style='margin-top:8px;'>
                        <b>{row['Event']}</b><br>
                        <small>{row['Date']} | {row['Type']}</small>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 3, 1])
            status = c1.selectbox("Action", ["Pending", "Validate", "Cancelled"], key=f"s_{index}")
            
            reason = ""
            if status == "Cancelled":
                reason = c2.text_input("Why cancel?", key=f"r_{index}")
            
            if c3.button("Submit", key=f"b_{index}"):
                if status != "Pending":
                    new_entry = {
                        "Date": row["Date"], "Time": row["Time"], "Event": row["Event"], 
                        "Type": row["Type"], "Status": status, "Reason": reason
                    }
                    st.session_state.master_log = pd.concat([st.session_state.master_log, pd.DataFrame([new_entry])], ignore_index=True)
                    st.session_state.current_search = st.session_state.current_search.drop(index)
                    st.rerun()

# --- ADMIN VIEW ---
elif role == "Admin":
    st.title("🛠️ Admin Master Log")
    
    if st.session_state.master_log.empty:
        st.write("No processed events yet.")
    else:
        # Displaying the log with Time column
        st.dataframe(
            st.session_state.master_log,
            column_order=("Date", "Time", "Event", "Type", "Status", "Reason"),
            use_container_width=True,
            hide_index=True
        )
        
        csv = st.session_state.master_log.to_csv(index=False).encode('utf-8')
        st.download_button("Download Admin CSV", csv, "aifi_full_log.csv")
