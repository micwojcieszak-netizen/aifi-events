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
    .stButton>button { background-color: #007BFF; color: white; border-radius: 20px; width: 100%; }
    .event-box { 
        padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e1e4e8;
    }
    .status-pending { border-left: 5px solid #ffc107; background: #fffdf5; }
    .status-validate { border-left: 5px solid #28a745; background: #f4fff6; }
    .status-cancelled { border-left: 5px solid #dc3545; background: #fff5f5; }
    .time-badge { background-color: #e7f3ff; color: #007BFF; padding: 2px 8px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SEARCH ENGINE (Simulating 3 Month Scan) ---
def ai_scan_3_months():
    teams = ["Arsenal", "Chelsea", "Man City", "Liverpool", "Spurs", "Newcastle"]
    data = []
    for _ in range(8): # Generate 8 events
        days_ahead = random.randint(1, 90)
        date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        data.append({
            "Date": date, "Time": random.choice(["12:30", "15:00", "20:00"]),
            "Event": f"AVFC vs {random.choice(teams)}", "Type": "Premier League",
            "Status": "Pending", "Reason": ""
        })
    df = pd.DataFrame(data).sort_values(["Date", "Time"])
    return df

# --- STATE MANAGEMENT ---
if 'master_data' not in st.session_state:
    st.session_state.master_data = ai_scan_3_months()

# --- SIDEBAR ---
with st.sidebar:
    st.title("AIfi Control")
    role = st.radio("Access Level:", ["Client", "Admin"])
    if role == "Admin":
        if st.text_input("Admin Password", type="password") != "aifi2026": st.stop()
    
    st.divider()
    if st.button("🔄 Rescan Live Events (3 Months)"):
        st.session_state.master_data = ai_scan_3_months()
        st.success("Calendar Refreshed!")
        st.rerun()

# --- UNIFIED CLIENT VIEW ---
if role == "Client":
    st.title("⚽ AVFC Event Manager")
    st.info("Showing all events for the next 3 months. Update statuses below.")

    for index, row in st.session_state.master_data.iterrows():
        # Determine Box Style
        box_class = f"status-{row['Status'].lower()}"
        
        st.markdown(f"""
            <div class='event-box {box_class}'>
                <span class='time-badge'>🕒 {row['Time']}</span> &nbsp; <b>{row['Event']}</b><br>
                <small>{row['Date']} | {row['Type']} | <b>Current Status: {row['Status']}</b></small>
            </div>
        """, unsafe_allow_html=True)

        # Inline controls for each event
        c1, c2, c3 = st.columns([2, 4, 1])
        
        # Status selector defaults to current status
        status_options = ["Pending", "Validate", "Cancelled"]
        new_status = c1.selectbox("Change Status", status_options, 
                                 index=status_options.index(row['Status']), 
                                 key=f"s_{index}")
        
        # Comment field
        new_reason = c2.text_input("Comment / Reason", value=row['Reason'], 
                                  key=f"r_{index}", placeholder="Add notes here...")
        
        # Update Button
        if c3.button("Save", key=f"b_{index}"):
            st.session_state.master_data.at[index, "Status"] = new_status
            st.session_state.master_data.at[index, "Reason"] = new_reason
            st.toast(f"Updated {row['Event']}")
            st.rerun()

# --- ADMIN VIEW (UNTOUCHED) ---
elif role == "Admin":
    st.title("🛠️ Admin Master Log")
    st.write("Summary of all event statuses.")
    
    # Filter only handled events for the log view
    handled_df = st.session_state.master_data[st.session_state.master_data["Status"] != "Pending"]
    
    if handled_df.empty:
        st.warning("Client has not validated any events yet.")
    else:
        st.dataframe(handled_df, use_container_width=True, hide_index=True)
        
        csv = handled_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Report (CSV)", csv, "aifi_admin_report.csv")
