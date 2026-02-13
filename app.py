import streamlit as st
import os
import pandas as pd
import plotly.express as px
from src.data_provider import get_all_test_data, get_log_content
from src.components import render_metrics, render_charts, highlight_logs

# Nastavení stránky
st.set_page_config(page_title="Maestro Fix", layout="wide")

# Načtení dat
df = get_all_test_data()

st.title("Maestro Dashboard (Mac Fix ModeS)")

if df.empty:
    st.error("Data nenalezena v logs/logs/!")
    st.stop()

# Výběr běhu
st.info("Nejdříve vyberte běh, který chcete zkoumat:")
available_runs = sorted(df['run_id'].unique(), reverse=True)

# Použijeme radio buttony 
selected_run = st.radio(
    "Dostupné běhy:",
    options=available_runs[:19], # Všechny běhy
    horizontal=True,
    key="fix_radio_selection"
)

st.divider()

# Data pro vybraný běh
run_df = df[df['run_id'] == selected_run].copy()

# Metriky a grafy jen pro ten jeden vybraný běh
st.header(f"Statistiky pro běh: {selected_run}")
render_metrics(run_df)
render_charts(run_df)

st.divider()

# Seznam testů
st.header("🔎 Jednotlivé testy")

for i, row in run_df.iterrows():
    status_icon = "✅" if row['status'] == "Passed" else "🔴"
    
    # Zkusíme použít tlačítko místo expanderu
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
                    st.image(img_path)
                else:
                    st.caption("Snímek nenalezen.")

        st.tabs(["Logs"])[0].write(get_log_content(row['folder_path'], "console_output.log"))