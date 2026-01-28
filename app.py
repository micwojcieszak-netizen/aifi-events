import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import random

# --- AIfi VISUALS ---
st.set_page_config(page_title="AIfi Events Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #007BFF !important; }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 20px; }
    .event-box { padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e1e4e8; }
    .status-pending { border-left: 5px solid #ffc107; background: #fffdf5; }
    .status-validate { border-left: 5px solid #28a745; background: #f4fff6; }
    .status-cancelled { border-left: 5px solid #dc3545; background: #fff5f5; }
    .time-badge { background-color: #e7f3ff; color: #007BFF; padding: 2px 8px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DB FILE PATH ---
DB_FILE = "event_database.csv"

# --- CORE FUNCTIONS: LOAD / SAVE ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Initial empty state if no file exists
        return pd.DataFrame(columns=["Date", "Time", "Event", "Type", "Status", "Reason"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def ai_scan_3_months(existing_df):
    teams = ["Arsenal", "Chelsea", "Man City", "Liverpool", "Spurs"]
    new_rows = []
    for _ in range(5):
        days_ahead = random.randint(1, 90)
        date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        event_name = f"AVFC vs {random.choice(teams)}"
        
        # Avoid duplicates
        if event_name not in existing_df['Event'].values:
            new_rows.append({
                "Date": date, "Time": random.choice(["15:00", "20:00"]),
                "Event": event_name, "Type": "Premier League",
                "Status": "Pending", "Reason": ""
            })
    
    combined = pd.concat([existing_df, pd.DataFrame(new_rows)], ignore_index=True)
    return combined.sort_values(["Date", "Time"])

# --- DATA INITIALIZATION ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("AIfi Control")
    role = st.radio("Access Level:", ["Client", "Admin"])
    if role == "Admin":
        if st.text_input("Admin Password", type="password") != "aifi2026": st.stop()
    
    st.divider()
    if st.button("🔄 Rescan Live Events (3 Months)"):
        st.session_state.master_data = ai_scan_3_months(st.session_state.master_data)
        save_data(st.session_state.master_data)
        st.success("New events added to database!")
        st.rerun()

# --- UNIFIED CLIENT VIEW ---
if role == "Client":
    st.title("⚽ AVFC Event Manager")
    
    if st.session_state.master_data.empty:
        st.info("No events found. Please use 'Rescan' in the sidebar.")
    
    for index, row in st.session_state.master_data.iterrows():
        box_class = f"status-{row['Status'].lower()}"
        
        st.markdown(f"""
            <div class='event-box {box_class}'>
                <span class='time-badge'>🕒 {row['Time']}</span> &nbsp; <b>{row['Event']}</b><br>
                <small>{row['Date']} | {row['Type']} | <b>Current Status: {row['Status']}</b></small>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 4, 1])
        status_options = ["Pending", "Validate", "Cancelled"]
        
        # Handle index for selectbox
        current_idx = status_options.index(row['Status']) if row['Status'] in status_options else 0
        
        new_status = c1.selectbox("Change Status", status_options, index=current_idx, key=f"s_{index}")
        new_reason = c2.text_input("Comment", value=str(row['Reason']) if pd.notna(row['Reason']) else "", key=f"r_{index}")
        
        if c3.button("Save", key=f"b_{index}"):
            st.session_state.master_data.at[index, "Status"] = new_status
            st.session_state.master_data.at[index, "Reason"] = new_reason
            save_data(st.session_state.master_data) # SAVE TO DISK
            st.toast("Saved to Database!")
            st.rerun()

# --- ADMIN VIEW ---
elif role == "Admin":
    st.title("🛠️ Admin Master Log")
    
    # Show only handled events
    handled_df = st.session_state.master_data[st.session_state.master_data["Status"] != "Pending"]
    
    if handled_df.empty:
        st.warning("No validated/cancelled events found.")
    else:
        st.dataframe(handled_df, use_container_width=True, hide_index=True)
        st.download_button("Download Database (CSV)", handled_df.to_csv(index=False).encode('utf-8'), "aifi_db.csv")
