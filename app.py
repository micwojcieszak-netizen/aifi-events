import streamlit as st
import pandas as pd
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
        padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #e1e4e8;
    }
    .status-valid { border-left: 5px solid #28a745; background: #f4fff6; }
    .status-cancelled { border-left: 5px solid #dc3545; background: #fff5f5; }
    .time-badge { background-color: #e7f3ff; color: #007BFF; padding: 2px 8px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIMULATED DATA FETCH ---
def ai_scan_3_months():
    teams = ["Arsenal", "Chelsea", "Man City", "Liverpool", "Spurs"]
    new_events = []
    for _ in range(3):
        days_ahead = random.randint(1, 90)
        date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        new_events.append({
            "Date": date, "Time": random.choice(["15:00", "20:00"]),
            "Event": f"AVFC vs {random.choice(teams)}", "Type": "Premier League"
        })
    return pd.DataFrame(new_events)

# --- STATE MANAGEMENT ---
if 'master_log' not in st.session_state:
    st.session_state.master_log = pd.DataFrame(columns=["Date", "Time", "Event", "Type", "Status", "Reason"])

if 'current_search' not in st.session_state:
    st.session_state.current_search = ai_scan_3_months()

# --- SIDEBAR ---
with st.sidebar:
    st.title("AIfi Control")
    role = st.radio("Access Level:", ["Client", "Admin"])
    if role == "Admin":
        if st.text_input("Pass", type="password") != "aifi2026": st.stop()
    
    if st.button("🔄 Rescan Live Events"):
        st.session_state.current_search = ai_scan_3_months()
        st.rerun()

# --- MAIN INTERFACE ---
st.title("⚽ AIfi Event Hub")

# SECTION 1: NEW EVENTS
st.subheader("🆕 New Discoveries")
if st.session_state.current_search.empty:
    st.write("No new events to review.")
else:
    for index, row in st.session_state.current_search.iterrows():
        with st.container():
            c1, c2, c3, c4 = st.columns([3, 2, 3, 1])
            c1.markdown(f"**{row['Event']}**<br><span class='time-badge'>{row['Time']}</span> | {row['Date']}", unsafe_allow_html=True)
            status = c2.selectbox("Action", ["Pending", "Validate", "Cancelled"], key=f"new_s_{index}")
            reason = c3.text_input("Comment/Reason", key=f"new_r_{index}", placeholder="Optional for validate, required for cancel")
            
            if c4.button("Submit", key=f"new_b_{index}"):
                if status != "Pending":
                    new_row = pd.DataFrame([{"Date": row["Date"], "Time": row["Time"], "Event": row["Event"], "Type": row["Type"], "Status": status, "Reason": reason}])
                    st.session_state.master_log = pd.concat([st.session_state.master_log, new_row], ignore_index=True)
                    st.session_state.current_search = st.session_state.current_search.drop(index)
                    st.rerun()

st.divider()

# SECTION 2: PROCESSED EVENTS (The History)
st.subheader("📋 Processed Events")
if st.session_state.master_log.empty:
    st.info("No events have been processed yet.")
else:
    for index, row in st.session_state.master_log.iterrows():
        # Determine CSS class based on status
        css_class = "status-valid" if row["Status"] == "Validate" else "status-cancelled"
        
        st.markdown(f"""
            <div class='event-box {css_class}'>
                <strong>{row['Status']}</strong>: {row['Event']} | {row['Date']} at {row['Time']}<br>
                <small>Current Comment: {row['Reason'] if row['Reason'] else 'No comment provided'}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Admin/Client can change status here
        with st.expander("Change Status or Comment"):
            c1, c2, c3 = st.columns([2, 4, 1])
            new_status = c1.selectbox("New Status", ["Validate", "Cancelled"], index=0 if row["Status"]=="Validate" else 1, key=f"edit_s_{index}")
            new_reason = c2.text_input("New Comment", value=row["Reason"], key=f"edit_r_{index}")
            if c3.button("Update", key=f"edit_b_{index}"):
                st.session_state.master_log.at[index, "Status"] = new_status
                st.session_state.master_log.at[index, "Reason"] = new_reason
                st.success("Updated!")
                st.rerun()
