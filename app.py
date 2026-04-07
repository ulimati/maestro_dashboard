import streamlit as st
import os
import pandas as pd
import datetime
from streamlit_calendar import calendar
from src.data_provider import get_all_test_data, get_log_content
from src.components import render_metrics, render_charts
from src.db import get_user_by_email, get_role, verify_user

st.set_page_config(page_title="Maestro Fix", layout="wide")

# --- LOGIN PAGE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; padding: 60px 0 20px 0;">
            <h1 style="font-size: 3rem;">Maestro Dashboard</h1>
            <p style="color: #8e8e93;">Please log in to continue</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        email_input = st.text_input("Email")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Log in", use_container_width=True):
            user = verify_user(email_input, password_input)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.role = user["role"]
                st.session_state.name = user["name"]
                st.session_state.show_dashboard = False
                st.session_state.show_empty = False
                st.rerun()
            else:
                st.error("Invalid email or password.")
    st.stop()

# --- SIDEBAR (jen po přihlášení) ---
st.sidebar.write(f"👤 {st.session_state.name}")
st.sidebar.write(f"Role: {st.session_state.role}")
if st.sidebar.button("Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()

if st.sidebar.button("Log out", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# --- LANDING PAGE ---
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

# --- SECOND PAGE (Škoda) ---
if st.session_state.show_empty:
    if st.button("← Back"):
        st.session_state.show_empty = False
        st.rerun()
    st.title("Škoda")
    st.info("This section is empty. Content for the Škoda project can be placed here.")
    st.stop()

# --- BACK BUTTON FOR VW DASHBOARD ---
if st.button("← Back"):
    st.session_state.show_dashboard = False
    st.rerun()

# --- CSS FOR CALENDAR AND UI ---
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

# --- HEADER AND PLATFORM SELECTION ---
head_col, icon_col = st.columns([4, 1.5])

with head_col:
    st.title("Maestro Dashboard")

with icon_col:
    st.write("")
    if "selected_platform" not in st.session_state:
        st.session_state.selected_platform = "Android"
        
    platform = st.radio(
        "Platform:",
        ["Android", "iOS", "API"],
        horizontal=True,
        label_visibility="collapsed",
        key="selected_platform"
    )

# ================================================================
# SECTION 1: API TEST REPORT
# ================================================================
if "API" in platform:
    st.divider()
    df_api = get_all_test_data("⚙️ API")

    if df_api.empty:
        st.warning("⚠️ No API data found in the `logs/json` folder.")
        st.stop()

    current_time = datetime.datetime.now().strftime("%d. %m. %Y %H:%M:%S")
    st.markdown(f"### ⚙️ In-App Shop Cart API Test Report")
    st.caption(f"Updated: {current_time}")

    render_metrics(df_api)

    if st.session_state.role != "viewer":
        tab_summary, tab_all = st.tabs([
            "📊 Summary charts",
            f"📑 All results ({len(df_api)})"
        ])

        with tab_summary:
            clicked_status_api = render_charts(df_api, key_suffix="api_main")
            
            if clicked_status_api:
                st.divider()
                st.markdown(f"### Results for status: {clicked_status_api}")
                df_filtered_api = df_api[df_api['status'] == clicked_status_api]
                unique_tests = df_filtered_api['test_name'].unique()
                cols = st.columns(2)
                for i, name in enumerate(unique_tests):
                    test_data = df_filtered_api[df_filtered_api['test_name'] == name]
                    folder_icon = "❌" if (test_data['status'] == 'Failed').any() else "✅"
                    with cols[i % 2]:
                        with st.expander(f"{folder_icon} 📁 {name} ({len(test_data)} results)"):
                            for _, row in test_data.iterrows():
                                icon = "✅" if row['status'] == "Passed" else "❌"
                                with st.container(border=True):
                                    st.write(f"**{icon} Run ID:** `{row.get('run_id', 'N/A')}`")
                                    st.caption(f"Duration: {row.get('duration', 0)}s")
                                if st.session_state.role == "admin":
                                    if row['status'] == 'Failed':
                                        st.error(f"Error: {row.get('error_msg', 'Unknown error')}")
                                    with st.expander("Show JSON detail"):
                                        st.json(row.to_dict())

        with tab_all:
            unique_tests = df_api['test_name'].unique()
            cols = st.columns(2)
            for i, name in enumerate(unique_tests):
                test_data = df_api[df_api['test_name'] == name]
                total_in_test = len(test_data)
                failed_in_test = len(test_data[test_data['status'] == "Failed"])
                folder_icon = "❌" if failed_in_test > 0 else "✅"
                with cols[i % 2]:
                    with st.expander(f"{folder_icon} 📁 {name} ({total_in_test} runs)"):
                        for _, row in test_data.iterrows():
                            run_icon = "✅" if row['status'] == "Passed" else "❌"
                            with st.container(border=True):
                                st.write(f"**{icon} Run ID:** `{row.get('run_id', 'N/A')}`")
                                st.caption(f"Duration: {row.get('duration', 0)}s")
                            if st.session_state.role == "admin":
                                if row['status'] == 'Failed':
                                    st.error(f"Error: {row.get('error_msg', 'Unknown error')}")
                                with st.expander("Show JSON detail"):
                                    st.json(row.to_dict())

    st.stop()

# =================================================================
# SECTION 2: MOBILE TESTS (Android / iOS)
# =================================================================
df = get_all_test_data(platform)

if df.empty:
    st.warning(f"⚠️ No data found for {platform}.")
    st.stop()

df['date'] = df['run_id'].str[:10]

# --- CALENDAR AND DATE SELECTION ---
col_cal, col_info, _ = st.columns([0.7, 1, 1])

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = df['date'].max()

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
    events = [{"title": "", "start": d, "display": "block", "color": "#ff453a"} for d in df['date'].unique()]
    
    if selected_date:
        events.append({
            "start": selected_date,
            "display": "background",
            "backgroundColor": "#3984de"
        })

    cal_options = {
        "headerToolbar": {"left": "prev", "center": "title", "right": "next"},
        "initialView": "dayGridMonth",
        "height": 380,
        "firstDay": 1,
        "locale": "en",
    }
    state = calendar(events=events, options=cal_options, key="maestro_calendar")

available_runs = sorted(df[df['date'] == selected_date]['run_id'].unique(), reverse=True)
selected_run = None
with col_info:
    st.subheader(f"📅 Runs for: {selected_date}")
    selected_run = st.selectbox(
        "Select a specific test run:",
        available_runs if available_runs else ["No runs available"],
        key="selectbox_run_picker"
    )
st.divider()

# =================================================================
# SECTION 3: STATISTICS AND DETAILS
# =================================================================

def display_test_folders(data_to_display):
    unique_tests = data_to_display['test_name'].unique()
    cols = st.columns(2)
    data_to_display = data_to_display.reset_index(drop=True)
    
    for i, name in enumerate(unique_tests):
        test_data = data_to_display[data_to_display['test_name'] == name]
        total_in_test = len(test_data)
        failed_in_test = len(test_data[test_data['status'] == "Failed"])
        icon = "❌" if failed_in_test > 0 else "✅"
        label = "failures" if failed_in_test > 0 else "runs"
        
        with cols[i % 2]:
            with st.expander(f"{icon} {name} ({total_in_test} {label})"):
                
                for _, row in test_data.head(20).iterrows():
                    status_icon = "✅" if row['status'] == "Passed" else "❌"
                    st.write(f"**{status_icon} {row.get('run_id', 'N/A')}** | {row.get('duration', 0)}s")
                    
                    if row['status'] == "Failed":
                        if st.session_state.role == "admin":
                            st.error(f"Error: {row.get('error_msg', 'Unknown error')}")

                if len(test_data) > 20:
                    st.caption(f"⚠️ Zobrazeno pouze 20 nejnovějších záznamů z {len(test_data)} pro udržení rychlosti.")

# --- GLOBAL STATISTICS ---
with st.expander("📊 GLOBAL HISTORY (ENTIRE PLATFORM)", expanded=True):
    total_all = len(df)
    passed_all = len(df[df['status'] == "Passed"])
    failed_all = len(df[df['status'] == "Failed"])
    rate_all = (passed_all / total_all * 100) if total_all > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total tests", total_all)
    m2.metric("Passed", passed_all)
    m3.metric("Failed", failed_all)
    m4.metric("Success Rate", f"{rate_all:.1f}%")

    can_interact = st.session_state.role != "viewer"
    clicked_status_global = render_charts(df, key_suffix="global", show_selector=can_interact)

    if can_interact:
        if clicked_status_global:
            st.divider()
            st.markdown(f"### Results for status: {clicked_status_global}")
            df_filtered_global = df[df['status'] == clicked_status_global]
            display_test_folders(df_filtered_global)

# --- RUN DETAIL ---
if st.session_state.role != "viewer":
    if selected_run and selected_run != "No runs available":
        st.divider()
        with st.expander(f"🔎 RUN DETAIL: {selected_run}", expanded=True):
            run_df = df[df['run_id'] == selected_run].copy()

            passed_run = len(run_df[run_df['status'] == "Passed"])
            failed_run = len(run_df[run_df['status'] == "Failed"])

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total tests", len(run_df))
            m2.metric("Passed", passed_run)
            m3.metric("Failed", failed_run)
            m4.metric("Success Rate", f"{(passed_run / len(run_df) * 100):.1f}%")

            clicked_status_single = render_charts(run_df, key_suffix="single_run")
            
            st.divider()
            
            if clicked_status_single:
                st.markdown(f"### Test steps: {clicked_status_single}")
                
                run_df_filtered = run_df[run_df['status'] == clicked_status_single]
                run_df_filtered = run_df_filtered.reset_index(drop=True)
                cols = st.columns(2)
                
                for i, row in run_df_filtered.iterrows():
                    status_icon = "✅" if row['status'] == "Passed" else "❌"
                    with cols[i % 2]:
                        with st.expander(f"{status_icon} {row['test_name']} | {row['duration']}s"):
                            st.write(f"**Status:** {row['status']}")
                            
                            if row['status'] == "Failed":
                                if st.session_state.role == "admin":
                                    st.error(f"Error: {row.get('error_msg', 'Unknown error')}")
                                    
                                    img_path = os.path.join(row.get('folder_path', ''), f"fail_{row.get('test_name', '')}.png")
                                    if os.path.exists(img_path):
                                        st.image(img_path, caption=f"Failure screenshot - {row['test_name']}")
                            
                            if st.session_state.role == "admin":
                                log_content = get_log_content(row.get('folder_path', ''), "console_output.log")
                                if log_content:
                                    with st.expander("Show log"):
                                        st.code("".join(log_content), language="log")