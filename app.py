import streamlit as st
import pandas as pd
import time

# --- KONFIGURACJA WYGLĄDU AIfi ---
st.set_page_config(page_title="AIfi POC | AVFC Events", layout="wide")

st.markdown("""
    <style>
    /* Tło i główny kolor */
    .stApp { background-color: #ffffff; }
    
    /* Nagłówki */
    h1, h2, h3 { color: #007BFF !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Stylizacja przycisku głównego */
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: #e0e0e0;
    }

    /* Stylizacja tabeli i kart */
    .event-card {
        background-color: #f8f9fa;
        border-left: 5px solid #007BFF;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIKA POC ---

st.title("⚽ AIfi Event Intelligence: AVFC")
st.write("System monitorowania wydarzeń dla Aston Villa FC (Proof of Concept)")

# Sidebar dla ustawień
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Aston_Villa_FC_crest_%282016%29.svg/1200px-Aston_Villa_FC_crest_%282016%29.svg.png", width=100)
    st.info("Status: Połączono z silnikiem AI")
    target_url = st.text_input("URL do skanowania", value="https://www.avfc.co.uk/matches")

# Inicjalizacja danych w sesji
if 'data' not in st.session_state:
    st.session_state.data = None

# Przycisk akcji
if st.button("🔍 URUCHOM SKANOWANIE AI"):
    with st.spinner('Agent AI analizuje stronę biletową i kalendarz...'):
        # Symulacja pracy Firecrawl + Gemini
        time.sleep(2) 
        
        # Mock-up danych wyciągniętych przez AI
        raw_results = [
            {"Data": "2026-02-01", "Wydarzenie": "Aston Villa vs Brentford", "Typ": "Premier League", "Valid": False},
            {"Data": "2026-02-14", "Wydarzenie": "Aston Villa vs Liverpool", "Typ": "Premier League", "Valid": False},
            {"Data": "2026-02-28", "Wydarzenie": "Event: Hospitality Tour Villa Park", "Typ": "Inne", "Valid": False},
            {"Data": "2026-03-05", "Wydarzenie": "Aston Villa vs RB Leipzig", "Typ": "Champions League", "Valid": False},
        ]
        st.session_state.data = pd.DataFrame(raw_results)
        st.success("Znaleziono 4 nowe wydarzenia!")

# Wyświetlanie wyników
if st.session_state.data is not None:
    st.subheader("Znalezione eventy")
    
    # Tworzymy nagłówki kolumn
    head1, head2, head3, head4 = st.columns([2, 4, 2, 1])
    head1.markdown("**Data**")
    head2.markdown("**Wydarzenie**")
    head3.markdown("**Kategoria**")
    head4.markdown("**Status**")
    
    # Iteracja po danych
    for index, row in st.session_state.data.iterrows():
        c1, c2, c3, c4 = st.columns([2, 4, 2, 1])
        
        with c1:
            st.write(row["Data"])
        with c2:
            st.markdown(f"**{row['Wydarzenie']}**")
        with c3:
            st.caption(row["Typ"])
        with c4:
            # Checkbox dla klienta
            is_valid = st.checkbox("Valid", value=row["Valid"], key=f"check_{index}")
            st.session_state.data.at[index, "Valid"] = is_valid

    # Sekcja eksportu
    st.divider()
    if st.button("Zatwierdź i wyślij do raportu"):
        valid_count = st.session_state.data["Valid"].sum()
        if valid_count > 0:
            st.balloons()
            st.success(f"Raport wygenerowany! Przesłano {valid_count} zatwierdzonych eventów do bazy.")
        else:
            st.warning("Proszę zaznaczyć przynajmniej jeden valid event.")
