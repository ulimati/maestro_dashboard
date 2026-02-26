import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events

def render_metrics(df):
    """Vykreslí základní metriky testů."""
    total = len(df)
    success_count = len(df[df['status'] == 'Passed'])
    success_rate = (success_count / total * 100) if total > 0 else 0
    avg_time = df['duration'].mean() if total > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Celkem testů", total)
    c2.metric("Success Rate", f"{success_rate:.1f}%")
    c3.metric("Průměrná doba", f"{avg_time:.2f}s")

def render_charts(df, key_suffix=""):
    if df.empty:
        return None

    col1, col2 = st.columns(2)

    # unikátní klíč pro session_state
    clicked_key = f"clicked_status_{key_suffix}"
    if clicked_key not in st.session_state:
        st.session_state[clicked_key] = None

    # --- Pie chart: poměr Passed/Failed ---
    with col1:
        # počítáme přesně z tohoto df
        passed_count = len(df[df['status'] == 'Passed'])
        failed_count = len(df[df['status'] == 'Failed'])

        fig_pie = px.pie(
            names=['Passed', 'Failed'],
            values=[passed_count, failed_count],
            title="Poměr úspěšnosti",
            color=['Passed', 'Failed'],
            color_discrete_map={'Passed': '#2ecc71', 'Failed': '#e74c3c'},
            hole=0.4
        )

        event = plotly_events(
            fig_pie,
            click_event=True,
            hover_event=False,
            key=f"pie_{key_suffix}"
        )

        if event:
            point_index = event[0].get("pointNumber")
            if point_index is not None:
                st.session_state[clicked_key] = ['Passed', 'Failed'][point_index]

    # --- Bar chart: průměrné doby pro testy v této složce ---
    with col2:
        avg_times = df.groupby('test_name')['duration'].mean().reset_index()

        fig_bar = px.bar(
            avg_times,
            x='test_name',
            y='duration',
            title="Průměrná doba testů (s)"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    return st.session_state[clicked_key]

def highlight_logs(lines):
    """Vykreslí řádky logu s barevným zvýrazněním chyb."""
    if not lines or (len(lines) == 1 and "nebyl nalezen" in lines[0]):
        st.info(lines[0] if lines else "Log je prázdný.")
        return

    highlighted_html = ""
    for line in lines:
        safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        if any(word in safe_line.upper() for word in ["ERROR", "FATAL", "EXCEPTION", "FAIL"]):
            highlighted_html += f'<span style="color: #ff4b4b; font-weight: bold;">{safe_line}</span>'
        elif "WARN" in safe_line.upper():
            highlighted_html += f'<span style="color: #ffa500;">{safe_line}</span>'
        else:
            highlighted_html += safe_line
        
        if not safe_line.endswith('\n'):
            highlighted_html += "\n"

    st.markdown(
        f"""
        <div style="
            background-color: #0e1117; 
            color: #d1d1d1;
            padding: 15px; 
            border-radius: 5px; 
            border: 1px solid #30363d;
            font-family: 'Courier New', monospace; 
            white-space: pre-wrap; 
            font-size: 13px;
            max-height: 400px;
            overflow-y: auto;
            line-height: 1.4;
        ">
{highlighted_html}</div>
        """, 
        unsafe_allow_html=True
    )