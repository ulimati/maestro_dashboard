import streamlit as st
import os
import pandas as pd
import datetime
from streamlit_calendar import calendar
from src.data_provider import get_all_test_data, get_log_content
from src.components import render_metrics, render_charts

# Paměť pro zobrazení API reportu
if 'zobrazit_api_report' not in st.session_state:
    st.session_state.zobrazit_api_report = False

st.set_page_config(page_title="Maestro Fix", layout="wide")
# --- CSS ---
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
head_col, icon_col = st.columns([4, 1])

with head_col:
    st.title("Maestro Dashboard")

with icon_col:
    st.write("")
    platform = st.radio(
        "Platforma:",
        ["🤖 Android", "🍎 iOS"],
        horizontal=True,
        label_visibility="collapsed"
    )

if st.button("⚙️ Spustit API Testy", use_container_width=True):
    st.session_state.zobrazit_api_report = True

# --- NAČTENÍ DAT (Dynamicky podle platformy) ---
df = get_all_test_data(platform)

if df.empty:
    target_folder = "logs/logs_android" if "Android" in platform else "logs/logs_ios"
    st.warning(f"⚠️ Žádná data pro {platform} nebyla nalezena ve složce `{target_folder}`.")
    st.info("Ujistěte se, že složka existuje a obsahuje XML reporty.")
    st.stop()

df['date'] = df['run_id'].str[:10]

# --- 1. KALENDÁŘ A VÝBĚR DNE ---
col_cal, col_info, _ = st.columns([0.7, 1, 1])

with col_cal:
    events = [{"title": "", "start": d, "display": "block", "color": "#ff453a"} for d in df['date'].unique()]
    cal_options = {
        "headerToolbar": {"left": "prev", "center": "title", "right": "next"},
        "initialView": "dayGridMonth",
        "height": 380,
        "firstDay": 1,
        "locale": "cs",
    }
    state = calendar(events=events, options=cal_options, key="maestro_calendar")

if state.get("dateClick"):
    raw_date = pd.to_datetime(state["dateClick"]["date"]) + pd.Timedelta(hours=12)
    selected_date = raw_date.strftime('%Y-%m-%d')
elif state.get("eventClick"):
    raw_date = pd.to_datetime(state["eventClick"]["event"]["start"]) + pd.Timedelta(hours=12)
    selected_date = raw_date.strftime('%Y-%m-%d')
else:
    selected_date = df['date'].max()

available_runs = sorted(df[df['date'] == selected_date]['run_id'].unique(), reverse=True)
selected_run = None

with col_info:
    st.subheader(f"📅 Běhy pro: {selected_date}")
    if available_runs:
        selected_run = st.selectbox("Vyberte konkrétní testovací běh:", available_runs, key="run_selector")
    else:
        st.warning("V tento den neběžely žádné testy.")

st.divider()

# --- SEKCE: API TEST REPORT ---
if st.session_state.zobrazit_api_report:
    st.divider() # Oddělovací čára
    
    aktualni_cas = datetime.datetime.now().strftime("%d. %m. %Y %H:%M:%S")      
    st.markdown("### In-App Shop Cart API Test Report")
    st.caption(f"Generated: {aktualni_cas}")

    df_vysledky = get_all_test_data(st.session_state.get("vybrana_platforma", "Android"))

# Vsechny testy napric vsemi JSON soubory
    soucet_total = int(df_vysledky["total_tests"].sum()) if "total_tests" in df_vysledky.columns else 0
    soucet_passed = int(df_vysledky["passed_tests"].sum()) if "passed_tests" in df_vysledky.columns else 0
    soucet_failed = int(df_vysledky["failed_tests"].sum()) if "failed_tests" in df_vysledky.columns else 0
    soucet_skipped = 0

    # 4 Barevné boxy vedle sebe
    col_tot, col_pass, col_fail, col_skip = st.columns(4)
    with col_tot:
        st.info(f"TOTAL TESTS\n### {soucet_total}")
    with col_pass:
        st.success(f"PASSED\n### {soucet_passed}")
    with col_fail:
        st.error(f"FAILED\n### {soucet_failed}")
    with col_skip:
        st.warning(f"SKIPPED\n### {soucet_skipped}")

    st.markdown("#### Test Results")
    
 # 3. DYNAMICKÉ VYKRESLENÍ DETAILŮ (Smyčka přes všechny načtené JSONy)
    if df_vysledky.empty:
        st.info("Zatím tu nejsou žádné testy k zobrazení.")
    else:
        for index, row in df_vysledky.iterrows():
            with st.container(border=True):
                ikona = "✅" if row.get("status") == "Passed" else "❌"
                nazev_testu = row.get("test_name", "Neznámý test")
                
                st.markdown(f"##### {ikona} {nazev_testu}")
                st.write(f"**Status:** {row.get('status', 'N/A')}")
                st.write(f"**Duration:** {row.get('duration', 0)} ms")
                
                chyba = row.get("error_msg", "")
                if chyba:
                    st.error(f"**Error:** {chyba}")
                
                st.markdown("**Response:**")
                # data konkrétního testu
                st.json({
                    "test_id": row.get("test_id", ""),
                    "run_id": row.get("run_id", ""),
                    "file_path": row.get("folder_path", "")
                })
    
    # Tlačítko pro opětovné skrytí reportu
    if st.button("❌ Zavřít API Report"):
        st.session_state.zobrazit_api_report = False
        st.rerun() 
        
    st.divider()
# --- KONEC SEKCE API REPORTU ---

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
    render_charts(df, key_suffix="global")

# --- 3. DETAILNÍ STATISTIKA PRO VYBRANÝ BĚH ---
if selected_run:
    st.divider()
    with st.expander(f"🔎 DETAIL BĚHU: {selected_run}", expanded=True):
        run_df = df[df['run_id'] == selected_run].copy()
        render_metrics(run_df)
        render_charts(run_df, key_suffix="single_run")
        
        st.divider()
        st.subheader("Kroky testu")
        for i, row in run_df.iterrows():
            status_icon = "✅" if row['status'] == "Passed" else "🔴"
            with st.expander(f"{status_icon} {row['test_name']} | {row['duration']}s"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Stav:** {row['status']}")
                    if row['status'] == "Failed":
                        st.error(f"Chyba: {row['error_msg']}")
                with col2:
                    if row['status'] == "Failed":
                        # Cesta k obrázku (předpokládá název fail_ID.png)
                        img_path = os.path.join(row['folder_path'], f"fail_{row['test_id']}.png")
                        if os.path.exists(img_path):
                            st.image(img_path, caption=f"Snímek chyby - {row['test_name']}")
                        else:
                            st.info(f"Snímek nenalezen v: {img_path}")
                
                log_content = get_log_content(row['folder_path'], "console_output.log")
                st.code("".join(log_content), language="log")