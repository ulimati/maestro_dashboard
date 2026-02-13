import streamlit as st
import os
import pandas as pd
from streamlit_calendar import calendar
from src.data_provider import get_all_test_data, get_log_content
from src.components import render_metrics, render_charts, highlight_logs

st.set_page_config(page_title="Maestro Fix", layout="wide")

df = get_all_test_data()

if df.empty:
    st.error("❌ Data nenalezena!")
    st.stop()

df['date'] = df['run_id'].str[:10]

# --- CSS PRO KALENDÁŘ A IKONY ---
st.markdown("""
<style>
    .fc { background: #1c1c1e !important; border-radius: 18px; padding: 10px; border: none !important; color: white !important; font-size: 0.8rem; }
    .fc-toolbar-title { color: #ff453a !important; text-transform: uppercase; font-size: 0.9rem !important; font-weight: bold; }
    .fc-col-header-cell-cushion, .fc-daygrid-day-number { color: #ffffff !important; text-decoration: none !important; }
    .fc-daygrid-event { background-color: #ff453a !important; border-radius: 50% !important; width: 4px !important; height: 4px !important; margin: 0 auto !important; }
    .fc-theme-standard td, .fc-theme-standard th, .fc-scrollgrid { border: none !important; }
    .fc-button { background: transparent !important; border: none !important; color: #8e8e93 !important; padding: 0 !important; }
    
    /* Stylování pro platformy vpravo nahoře */
    .platform-box {
        text-align: right;
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- HLAVIČKA S IKONAMI ---
head_col, icon_col = st.columns([4, 1])

with head_col:
    st.title("Maestro Dashboard (Mac Fix Mode)")

with icon_col:
    st.write("")
    # Přepínač platformy (zatím jen vizuální)
    platform = st.radio(
        "Platforma:",
        ["🤖 Android", "🍎 iOS"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.write("---")
    is_dark = st.toggle("🌙 Dark Mode", value=True)

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
    st.subheader(f"📅 Výběr běhu pro den: {selected_date}")
    if available_runs:
        selected_run = st.selectbox("Vyberte konkrétní testovací běh:", available_runs, key="run_selector")
    else:
        st.warning("V tento den neběžely žádné testy.")

st.divider()

# --- 2. GLOBÁLNÍ STATISTIKA (Vždy viditelná a neměnná) ---
with st.expander("📊 STATISTIKA VŠECH TESTŮ (CELKOVÁ HISTORIE)", expanded=True):
    st.header("Globální přehled za všechna data")
    
    total_all = len(df)
    passed_all = len(df[df['status'] == "Passed"])
    failed_all = len(df[df['status'] == "Failed"])
    rate_all = (passed_all / total_all * 100) if total_all > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Celkem testů", total_all)
    m2.metric("Úspěšné", passed_all)
    m3.metric("Selhalo", failed_all)
    m4.metric("Success Rate", f"{rate_all:.1f}%")

    render_charts(df, key_suffix="global_history")

# --- 3. DETAILNÍ STATISTIKA PRO VYBRANÝ BĚH ---
if selected_run:
    st.divider()
    
    with st.expander(f"🔎 DETAILNÍ STATISTIKA PRO BĚH: {selected_run}", expanded=True):
        
        # Filtrace data POUZE pro tento jeden vybraný běh
        run_df = df[df['run_id'] == selected_run].copy()

        # Zobrazení metrik a grafů pro konkrétní běh
        render_metrics(run_df)
        render_charts(run_df, key_suffix="single_run_detail")
        
        st.divider()
        st.subheader("Průzkumník kroků vybraného testu")
        
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
                        img_path = os.path.join(row['folder_path'], f"fail_{row['test_id']}.png")
                        if os.path.exists(img_path):
                            st.image(img_path, caption="Snímek chyby")
                
                log_content = get_log_content(row['folder_path'], "console_output.log")
                st.code(log_content, language="log")