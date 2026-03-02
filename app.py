import streamlit as st
import os
import pandas as pd
import datetime
from streamlit_calendar import calendar
from src.data_provider import get_all_test_data, get_log_content
from src.components import render_metrics, render_charts

st.set_page_config(page_title="Maestro Fix", layout="wide")

# --- ÚVODNÍ STRÁNKA + VW tlacitko ---
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

if "show_empty" not in st.session_state:
    st.session_state.show_empty = False

if not st.session_state.show_dashboard and not st.session_state.show_empty:

    st.markdown("""
        <div style="text-align: center; padding: 80px 0;">
            <h1 style="font-size: 3rem;">Project</h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([2, 4, 1, 4, 2])
    with col2:
        if st.button("Volkswagen", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()
    with col4:
        if st.button("Škoda", use_container_width=True):
            st.session_state.show_empty = True
            st.rerun()
    st.stop()

# --- druhe tlacitko SKODA---
if st.session_state.show_empty:
    if st.button("Zpět"):
        st.session_state.show_empty = False
        st.rerun()
    st.title("Škoda")
    st.info("Tato část je prázdná. Zde může být obsah pro Škoda projekt.")
    st.stop()

if st.button("Zpět"):
    st.session_state.show_dashboard = False
    st.rerun()

# --- CSS PRO KALENDÁŘ A UI ---
st.markdown("""
<style>
    .fc { background: #1c1c1e !important; border-radius: 18px; padding: 10px; border: none !important; color: white !important; font-size: 0.8rem; }
    .fc-toolbar-title { color: #ff453a !important; text-transform: uppercase; font-size: 0.9rem !important; font-weight: bold; }
    .fc-col-header-cell-cushion, .fc-daygrid-day-number { color: #ffffff !important; text-decoration: none !important; }
    .fc-daygrid-event { background-color: #ff453a !important; border-radius: 50% !important; width: 4px !important; height: 4px !important; margin: 0 auto !important; }
    .fc-theme-standard td, .fc-theme-standard th, .fc-scrollgrid { border: none !important; }
    .fc-button { background: transparent !important; border: none !important; color: #8e8e93 !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# --- HLAVIČKA A VÝBĚR PLATFORMY ---
head_col, icon_col = st.columns([4, 1.5])

with head_col:
    st.title("Maestro Dashboard")

with icon_col:
    st.write("")
    # Použití session_state pro pamatování vybrané platformy
    if "selected_platform" not in st.session_state:
        st.session_state.selected_platform = "🤖 Android"
        
    platform = st.radio(
        "Platforma:",
        ["Android", "iOS", "API"],
        horizontal=True,
        label_visibility="collapsed",
        key="selected_platform" # Streamlit automaticky aktualizuje session_state
    )

# SEKCE 1: API TEST REPORT (Zobrazí se jen při volbě API)
if "API" in platform:
    st.divider()
    df_api = get_all_test_data("⚙️ API")

    if df_api.empty:
        st.warning("⚠️ Žádná API data nebyla nalezena ve složce `logs/json`.")
        st.stop()

    aktualni_cas = datetime.datetime.now().strftime("%d. %m. %Y %H:%M:%S")      
    st.markdown(f"### ⚙️ In-App Shop Cart API Test Report")
    st.caption(f"Aktualizováno: {aktualni_cas}")

    render_metrics(df_api)

    tab_summary, tab_all = st.tabs([
        "📊 Grafický přehled", 
        f"📑 Všechny výsledky ({len(df_api)})"
    ])

    with tab_summary:
        kliknuty_stav_api = render_charts(df_api, key_suffix="api_main")
        
        if kliknuty_stav_api:
            st.divider()
            st.markdown(f"### Výsledky pro stav: {kliknuty_stav_api}")
            df_filtered_api = df_api[df_api['status'] == kliknuty_stav_api]
            unikatni_testy = df_filtered_api['test_name'].unique()
            cols = st.columns(2)
            for i, nazev in enumerate(unikatni_testy):
                data_testu = df_filtered_api[df_filtered_api['test_name'] == nazev]
                with cols[i % 2]:
                    ikona_slozky = "❌" if (data_testu['status'] == 'Failed').any() else "✅"
                    with st.expander(f"{ikona_slozky} 📁 {nazev} ({len(data_testu)} výsledků)"):
                        for _, row in data_testu.iterrows():
                            ikona = "✅" if row['status'] == "Passed" else "❌"
                            with st.container(border=True):
                                st.write(f"**{ikona} Běh ID:** `{row.get('run_id', 'N/A')}`")
                                st.caption(f"Trvání: {row.get('duration', 0)}s")
                                if row['status'] == 'Failed':
                                    st.error(f"Chyba: {row.get('error_msg', 'Neznámá chyba')}")
                                with st.expander("Zobrazit JSON detail"):
                                    st.json(row.to_dict())

    with tab_all:
        unikatni_testy = df_api['test_name'].unique()
        cols = st.columns(2)
        for i, nazev in enumerate(unikatni_testy):
            data_testu = df_api[df_api['test_name'] == nazev]
            celkem_v_testu = len(data_testu)
            selhalo_v_testu = len(data_testu[data_testu['status'] == "Failed"])
            ikona_slozky = "❌" if selhalo_v_testu > 0 else "✅"
            with cols[i % 2]:
                with st.expander(f"{ikona_slozky} 📁 {nazev} ({celkem_v_testu} běhů)"):
                    for _, row in data_testu.iterrows():
                        ikona_behu = "✅" if row['status'] == "Passed" else "❌"
                        with st.container(border=True):
                            st.write(f"**{ikona_behu} Běh ID:** `{row.get('run_id', 'N/A')}`")
                            st.caption(f"Trvání: {row.get('duration', 0)}s")
                            if row['status'] == 'Failed':
                                st.error(f"Chyba: {row.get('error_msg', 'Neznámá chyba')}")
                            with st.expander("Zobrazit JSON detail"):
                                st.json(row.to_dict())


# SEKCE 2: MOBILNÍ TESTY (Android / iOS)
df = get_all_test_data(platform)

if df.empty:
    st.warning(f"⚠️ Žádná data pro {platform} nebyla nalezena.")
    st.stop()

df['date'] = df['run_id'].str[:10]

# --- KALENDÁŘ A VÝBĚR DNE ---
col_cal, col_info, _ = st.columns([0.7, 1, 1])

# 1. Zajištění uložení vybraného data ve st.session_state
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = df['date'].max()

# 2. Získání kliknutí PŘED vykreslením kalendáře
if "maestro_calendar" in st.session_state and st.session_state.maestro_calendar:
    cal_state = st.session_state.maestro_calendar
    if cal_state.get("dateClick"):
        raw_date = pd.to_datetime(cal_state["dateClick"]["date"]) + pd.Timedelta(hours=12)
        st.session_state.selected_date = raw_date.strftime('%Y-%m-%d')
    elif cal_state.get("eventClick"):
        raw_date = pd.to_datetime(cal_state["eventClick"]["event"]["start"]) + pd.Timedelta(hours=12)
        st.session_state.selected_date = raw_date.strftime('%Y-%m-%d')

selected_date = st.session_state.selected_date

with col_cal:
    # Tvé původní červené tečky pro dny s testy
    events = [{"title": "", "start": d, "display": "block", "color": "#ff453a"} for d in df['date'].unique()]
    
    # NOVÉ: Nativní obarvení pozadí vybraného dne do šeda
    if selected_date:
        events.append({
            "start": selected_date,
            "display": "background",
            "backgroundColor": "#3984de" # Zde je tvá šedá barva
        })

    cal_options = {
        "headerToolbar": {"left": "prev", "center": "title", "right": "next"},
        "initialView": "dayGridMonth",
        "height": 380,
        "firstDay": 1,
        "locale": "cs",
    }
    state = calendar(events=events, options=cal_options, key="maestro_calendar")

available_runs = sorted(df[df['date'] == selected_date]['run_id'].unique(), reverse=True)
selected_run = None
with col_info:
    st.subheader(f"📅 Běhy pro: {selected_date}")
    selected_run = st.selectbox("Vyberte konkrétní testovací běh:", available_runs if available_runs else ["Žádné běhy"],
    key="selectbox_vyber_behu"
    )
st.divider()

# SEKCE 3: STATISTIKA A DETAILY PRO GLOBALNÍ BĚH A PRO VYBRANÝ BĚH

# --- Pomocná funkce pro zobrazení složek testů (použitelná na více místech) ---
def zobrazeni_slozek_testu(data_k_zobrazeni):
    unikatni_testy = data_k_zobrazeni['test_name'].unique()
    cols = st.columns(2)
    data_k_zobrazeni = data_k_zobrazeni.reset_index(drop=True)
    
    for i, nazev in enumerate(unikatni_testy):
        data_testu = data_k_zobrazeni[data_k_zobrazeni['test_name'] == nazev]
        celkem_v_testu = len(data_testu)
        selhalo_v_testu = len(data_testu[data_testu['status'] == "Failed"])
        ikona = "❌" if selhalo_v_testu > 0 else "✅"
        popis = "selhání" if selhalo_v_testu > 0 else "běhů"
        
        with cols[i % 2]:
            with st.expander(f"{ikona} 📁 {nazev} ({celkem_v_testu} {popis})"):
                for _, row in data_testu.iterrows():
                    stav_ikona = "✅" if row['status'] == "Passed" else "❌"
                    st.write(f"**{stav_ikona} {row.get('run_id', 'N/A')}** | {row.get('duration', 0)}s")
                    
                    if row['status'] == "Failed":
                        st.error(f"Chyba: {row.get('error_msg', 'Neznámá chyba')}")
                        
                        img_path = os.path.join(row.get('folder_path', ''), f"fail_{row.get('test_name', '')}.png")
                        if os.path.exists(img_path):
                            st.image(img_path, caption=f"Snímek chyby - {row['test_name']}")
                        
                    log_content = get_log_content(row.get('folder_path', ''), "console_output.log")
                    if log_content:
                        with st.expander("Zobrazit log"):
                            st.code("".join(log_content), language="log")

# --- 2. GLOBÁLNÍ STATISTIKA ---
with st.expander("📊 GLOBÁLNÍ HISTORIE (CELÁ PLATFORMA)", expanded=True):
    total_all = len(df)
    passed_all = len(df[df['status'] == "Passed"])
    failed_all = len(df[df['status'] == "Failed"])
    rate_all = (passed_all / total_all * 100) if total_all > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Celkem testů", total_all)
    m2.metric("Úspěšné", passed_all)
    m3.metric("Selhalo", failed_all)
    m4.metric("Success Rate", f"{rate_all:.1f}%")

    kliknuty_stav_global = render_charts(df, key_suffix="global")

    if kliknuty_stav_global:
       st.divider()
       st.subheader(f"Vysledky pro stav: {kliknuty_stav_global}")
       df_filtered_global = df[df['status'] == kliknuty_stav_global]
       zobrazeni_slozek_testu(df_filtered_global)


# --- 3. DETAILNÍ STATISTIKA PRO VYBRANÝ BĚH ---
if selected_run and selected_run != "Žádné běhy":
    st.divider()
    with st.expander(f"🔎 DETAIL BĚHU: {selected_run}", expanded=True):
        run_df = df[df['run_id'] == selected_run].copy()

        passed_run = len(run_df[run_df['status'] == "Passed"])
        failed_run = len(run_df[run_df['status'] == "Failed"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Celkem testů", len(run_df))
        m2.metric("Úspěšné", passed_run)
        m3.metric("Selhalo", failed_run)
        m4.metric("Success Rate", f"{(passed_run / len(run_df) * 100):.1f}%")

        # Zachytíme kliknutí pro tento konkrétní běh
        kliknuty_stav_single = render_charts(run_df, key_suffix="single_run")
        
        st.divider()
        
        if kliknuty_stav_single:
            st.subheader(f"Kroky testu: {kliknuty_stav_single}")
            
            # FILTRACE: Vybereme pouze testy, které odpovídají kliknutí
            run_df_filtered = run_df[run_df['status'] == kliknuty_stav_single]
            
            # Resetujeme index, aby nám správně fungovalo střídání sloupců (0, 1, 2, 3...)
            run_df_filtered = run_df_filtered.reset_index(drop=True)
            
            # Vytvoření dvou sloupců pro samotné složky
            cols = st.columns(2)
            
            for i, row in run_df_filtered.iterrows():
                status_icon = "✅" if row['status'] == "Passed" else "❌"
                
                # Střídáme levý (cols[0]) a pravý (cols[1]) sloupec
                with cols[i % 2]:
                    with st.expander(f"{status_icon} 📁 {row['test_name']} | {row['duration']}s"):
                        
                        # -- Obsah uvnitř rozkliknuté složky --
                        st.write(f"**Stav:** {row['status']}")
                        
                        if row['status'] == "Failed":
                            st.error(f"Chyba: {row.get('error_msg', 'Neznámá chyba')}")
                            
                            img_path = os.path.join(row.get('folder_path', ''), f"fail_{row.get('test_name', '')}.png")
                            if os.path.exists(img_path):
                                st.image(img_path, caption=f"Snímek chyby - {row['test_name']}")
                        
                        log_content = get_log_content(row.get('folder_path', ''), "console_output.log")
                        if log_content:
                            with st.expander("Zobrazit log"):
                                st.code("".join(log_content), language="log")
st.stop()