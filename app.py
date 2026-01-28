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
    .event-row { padding: 10px; border-bottom: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE SIMULATION ---
if 'master_log' not in st.session_state:
    # This stores EVERYTHING ever handled
    st.session_state.master_log = pd.DataFrame(columns=["Date", "Event", "Type", "Status", "Reason"])

if 'current_search' not in st.session_state:
    # This stores only the results of the latest scan
    st.session_state.current_search = pd.DataFrame([
        {"Date": "2026-02-15", "Event": "AVFC vs Arsenal", "Type": "Premier League"},
        {"Date": "2026-02-22", "Event": "AVFC vs Chelsea", "Type": "Premier League"}
    ])

# --- SIDEBAR ---
with st.sidebar:
    st.title("AIfi Control")
    role = st.radio("Access Level:", ["Client", "Admin"])
    
    if role == "Admin":
        if st.text_input("Admin Password", type="password") != "aifi2026":
            st.stop()
    
    st.divider()
    if st.button("🔄 Rescan Live Events"):
        # Logic to fetch new data would go here
        st.success("New events loaded!")
        st.rerun()

# --- CLIENT VIEW ---
if role == "Client":
    st.title("⚽ Client Event Review")
    st.write("Review new discoveries and set their status.")

    for index, row in st.session_state.current_search.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 4])
            
            col1.markdown(f"**{row['Event']}**")
            col1.caption(f"{row['Date']} | {row['Type']}")
            
            # Action Selection
            status = col2.selectbox("Action", ["Pending", "Validate", "Cancelled"], key=f"stat_{index}")
            
            reason = ""
            if status == "Cancelled":
                reason = col3.text_input("Reason for cancellation?", key=f"re_{index}")
            
            # Submit specific item
            if col2.button("Submit Choice", key=f"btn_{index}"):
                new_entry = {
                    "Date": row["Date"],
                    "Event": row["Event"],
                    "Type": row["Type"],
                    "Status": status,
                    "Reason": reason
                }
                # Add to Admin's Master Log
                st.session_state.master_log = pd.concat([st.session_state.master_log, pd.DataFrame([new_entry])], ignore_index=True)
                # Remove from current view
                st.session_state.current_search = st.session_state.current_search.drop(index)
                st.success(f"Sent to Admin as {status}")
                time.sleep(1)
                st.rerun()

# --- ADMIN VIEW ---
elif role == "Admin":
    st.title("🛠️ Admin Master Log")
    st.write("Full history of client decisions.")

    if st.session_state.master_log.empty:
        st.info("No events processed by client yet.")
    else:
        # High-level stats
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Processed", len(st.session_state.master_log))
        c2.metric("Validated", len(st.session_state.master_log[st.session_state.master_log["Status"] == "Validate"]))
        c3.metric("Cancelled", len(st.session_state.master_log[st.session_state.master_log["Status"] == "Cancelled"]))

        # Stylized Data Table
        st.dataframe(
            st.session_state.master_log,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status", options=["Validate", "Cancelled"], required=True
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        csv = st.session_state.master_log.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Final History (CSV)", csv, "aifi_history.csv", "text/csv")
