import streamlit as st
import os
import pandas as pd
import datetime
from streamlit_calendar import calendar
from src.data_provider import get_all_test_data, get_log_content
from src.components import render_metrics, render_charts

st.set_page_config(page_title="Maestro Fix", layout="wide")

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
        ["🤖 Android", "🍎 iOS", "⚙️ API"],
        horizontal=True,
        label_visibility="collapsed",
        key="selected_platform" # Streamlit automaticky aktualizuje session_state
    )

# =================================================================
# SEKCE 1: API TEST REPORT (Zobrazí se jen při volbě API)
# =================================================================
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

    tab_summary, tab_failed, tab_all = st.tabs([
        "📊 Grafický přehled", 
        f"❌ Selhalo ({len(df_api[df_api['status'] == 'Failed'])})", 
        f"📑 Všechny výsledky ({len(df_api)})"
    ])

    with tab_summary:
        # Tady neřešíme klikání, necháme to tak, jak to bylo
        render_charts(df_api, key_suffix="api_main")

    with tab_failed:
        df_failed_only = df_api[df_api['status'] == "Failed"]
        
        if df_failed_only.empty:
            st.success("Žádné testy neselhaly! 🎉")
        else:
            unikatni_selhane_testy = df_failed_only['test_name'].unique()
            cols = st.columns(2)
            
            for i, nazev in enumerate(unikatni_selhane_testy):
                data_testu_selhani = df_failed_only[df_failed_only['test_name'] == nazev]
                
                pocet_selhani = len(data_testu_selhani)
                
                with cols[i % 2]:
                    with st.expander(f"❌ 📁 {nazev} ({pocet_selhani} selhání)"):
                        
                        # --- VÝPIS JEDNOTLIVÝCH BĚHŮ UVNITŘ SLOŽKY ---
                        for _, row in data_testu_selhani.iterrows():
                            
                            with st.container(border=True):
                                st.write(f"**❌ Běh ID:** `{row.get('run_id', 'N/A')}`")
                                st.caption(f"Trvání: {row.get('duration', 0)}ms")
                                
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
                # --- HLAVNÍ SLOŽKA PRO DANÝ NÁZEV TESTU ---
                with st.expander(f"{ikona_slozky} 📁 {nazev} ({celkem_v_testu} běhů)"):
                    
                    # --- VÝPIS JEDNOTLIVÝCH BĚHŮ UVNITŘ SLOŽKY ---
                    for _, row in data_testu.iterrows():
                        ikona_behu = "✅" if row['status'] == "Passed" else "❌"
                        
                        with st.container(border=True):
                            st.write(f"**{ikona_behu} Běh ID:** `{row.get('run_id', 'N/A')}`")
                            st.caption(f"Trvání: {row.get('duration', 0)}ms")
                            
                            if row['status'] == 'Failed':
                                st.error(f"Chyba: {row.get('error_msg', 'Neznámá chyba')}")
                            
                            with st.expander("Zobrazit JSON detail"):
                                st.json(row.to_dict())
    
    st.stop() 

# =================================================================
# SEKCE 2: MOBILNÍ TESTY (Android / iOS)
# =================================================================
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

# =================================================================
# SEKCE 3: STATISTIKA A DETAILY PRO GLOBALNÍ BĚH A PRO VYBRANÝ BĚH
# =================================================================

# --- Pomocná funkce pro zobrazení složek testů (použitelná na více místech) ---
def zobrazeni_slozek_testu(data_k_zobrazeni):
    unikatni_testy = data_k_zobrazeni['test_name'].unique()
    cols = st.columns(2)
    
    # Seřazení, aby indexy odpovídaly
    data_k_zobrazeni = data_k_zobrazeni.reset_index(drop=True)
    
    for i, nazev in enumerate(unikatni_testy):
        data_testu = data_k_zobrazeni[data_k_zobrazeni['test_name'] == nazev]
        
        celkem_v_testu = len(data_testu)
        selhalo_v_testu = len(data_testu[data_testu['status'] == "Failed"])
        
        # Určení ikony a nadpisu
        ikona = "❌" if selhalo_v_testu > 0 else "✅"
        popis = "selhání" if selhalo_v_testu > 0 else "běhů"
        
        with cols[i % 2]:
            with st.expander(f"{ikona} 📁 {nazev} ({celkem_v_testu} {popis})"):
                for _, row in data_testu.iterrows():
                    stav_ikona = "✅" if row['status'] == "Passed" else "❌"
                    st.write(f"**{stav_ikona} {row.get('run_id', 'N/A')}** | {row.get('duration', 0)}s")
                    
                    if row['status'] == "Failed":
                        st.error(f"Chyba: {row.get('error_msg', 'Neznámá chyba')}")
                        # Zde můžeš přidat screenshoty nebo logy, pokud jsou k dispozici


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


# =================================================================
# SEKCE 3: STATISTIKA A DETAILY PRO VYBRANÝ DEN
# =================================================================

st.divider()

if selected_date:
    st.subheader(f"📊 Přehled všech testů pro den: {selected_date}")
    
    day_df = df[df['date'] == selected_date].copy()
    
    if day_df.empty:
        st.info(f"Pro den {selected_date} nejsou k dispozici žádné testy.")
    else:
        render_metrics(day_df)
        
        # Vykreslení grafů a zachycení kliknutí
        kliknuty_stav_den = render_charts(day_df, key_suffix="vybrany_den")
        
        st.divider()
        
        # Zobrazení složek testů AŽ PO KLIKNUTÍ na výseč v grafu
        if kliknuty_stav_den:
            st.subheader(f"Kroky testu: {kliknuty_stav_den}")
            
            # 1. Filtrujeme data podle toho, zda se kliklo na Passed nebo Failed
            day_df_filtered = day_df[day_df['status'] == kliknuty_stav_den]
            
            # 2. Zjistíme unikátní názvy testů, abychom je mohli seskupit do složek
            unikatni_testy = day_df_filtered['test_name'].unique()
            
            # Vytvoření dvou sloupců vedle sebe
            cols = st.columns(2)
            
            # 3. Procházíme testy po názvech (nikoliv po jednotlivých bězích!)
            for i, nazev_testu in enumerate(unikatni_testy):
                
                # Získáme všechny běhy pro tento konkrétní test
                data_testu = day_df_filtered[day_df_filtered['test_name'] == nazev_testu]
                pocet_behu = len(data_testu)
                
                status_icon = "✅" if kliknuty_stav_den == "Passed" else "❌"
                
                # Střídáme levý a pravý sloupec
                with cols[i % 2]:
                    # ZDE JE TA ZMĚNA: Název složky teď vypadá přesně jako na screenshotu (9 běhů)
                    with st.expander(f"{status_icon} 📁 {nazev_testu} ({pocet_behu} běhů)"):
                        
                        # Až tady uvnitř složky vypíšeme jednotlivé běhy
                        for _, row in data_testu.iterrows():
                            beh_id = row['run_id'].split('_')[1] if '_' in row['run_id'] else row['run_id']
                            
                            st.write(f"**Běh ID: {beh_id}** | Doba: {row['duration']}s")
                            
                            if row['status'] == "Failed":
                                st.error(f"Chyba: {row.get('error_msg', 'Neznámá chyba')}")
                                
                                img_path = os.path.join(row.get('folder_path', ''), f"fail_{row.get('test_id', '')}.png")
                                if os.path.exists(img_path):
                                    st.image(img_path, caption=f"Snímek chyby")
                            
                            log_content = get_log_content(row.get('folder_path', ''), "console_output.log")
                            if log_content:
                                st.code("".join(log_content), language="log")
                                
                            st.divider() # Malá čára oddělující jednotlivé běhy uvnitř složky
                            
        else:
            st.info("👆 Pro zobrazení detailních kroků testu pro tento den klikněte na zelenou (Passed) nebo červenou (Failed) část grafu výše.")