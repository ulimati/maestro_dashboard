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
    platform = st.radio(
        "Platforma:",
        ["🤖 Android", "🍎 iOS", "⚙️ API"],
        horizontal=True,
        label_visibility="collapsed",
        key="platform_selector"
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

# Logika výběru data
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
    selected_run = st.selectbox("Vyberte konkrétní testovací běh:", available_runs if available_runs else ["Žádné běhy"])

st.divider()

# =================================================================
# SEKCE 3: STATISTIKA A DETAILY PRO GLOBALNÍ BĚH A PRO VYBRANÝ BĚH
# =================================================================

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
                        img_path = os.path.join(row['folder_path'], f"fail_{row['test_id']}.png")
                        if os.path.exists(img_path):
                            st.image(img_path, caption=f"Snímek chyby - {row['test_name']}")
                        else:
                            st.info(f"Snímek nenalezen v: {img_path}")
                
                log_content = get_log_content(row['folder_path'], "console_output.log")
                st.code("".join(log_content), language="log")