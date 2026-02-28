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

    with col1:
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']

        fig_pie = px.pie(
            df,
            names='status',
            title="Poměr úspěšnosti",
            color='status',
            color_discrete_map={'Passed': '#2ecc71', 'Failed': '#e74c3c'},
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{key_suffix}")
        
        moznosti = ["— Vyberte stav —"] + list(status_counts['status'].values)
        vyber = st.selectbox("Zobrazit složky pro:", moznosti, key=f"select_{key_suffix}")

    with col2:
        avg_times = df.groupby('test_name')['duration'].mean().reset_index()
        fig_bar = px.bar(
            avg_times,
            x='test_name',
            y='duration',
            title="Průměrná doba testů (s)",
            labels={'test_name': 'Název testu', 'duration': 'Čas (s)'}
        )
        fig_bar.update_traces(marker_color='#3498db')
        st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{key_suffix}")

    if vyber == "— Vyberte stav —":
        return None
    return vyber

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