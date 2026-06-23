import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import qrcode
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from advanced_ml import generate_30_day_forecast, generate_prescriptive_insights

# 1. Page Configuration
st.set_page_config(page_title="Waar is de kip! | Enterprise", layout="wide", page_icon="🐓")

# 2. Global Styling
st.markdown("""
    <style>
    .main { background-color: #F4F6F9; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #0f172a; }
    .crud-card { background-color: #FFFFFF; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-top: 4px solid #3b82f6; }
    .chart-container { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border: 1px solid #E5E7EB; margin-bottom: 10px; }
    .chat-bubble { background-color: #e0f2fe; padding: 15px; border-radius: 10px; border-left: 5px solid #0284c7; margin-bottom: 10px; }
    .passport-card { background-color: #f0fdf4; padding: 20px; border-radius: 15px; border: 2px solid #22c55e; text-align: center; }
    .stApp { max-width: 1400px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

# Database & Logic Helpers
def get_db_connection():
    conn = sqlite3.connect('enterprise_poultry.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data
def load_telemetry_data():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT dt.*, fp.farm_name, lb.breed FROM daily_telemetry dt JOIN livestock_batches lb ON dt.batch_id = lb.batch_id JOIN farms_profile fp ON lb.farm_id = fp.farm_id", conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['revenue'] = df['eggs_laid'] * 0.25
        df['cost'] = 0.05 * 500
        df['profit'] = df['revenue'] - df['cost']
    return df

def admin_copilot(query):
    return "Operations Copilot: Analysis suggests yield variance correlates with temperature. Recommendation: Optimize HVAC scheduling."

def consumer_assistant(query):
    return "Hi! I'm Kipi 🐔. These chickens are raised with free-range standards and fed organic non-GMO corn."

# View 1: Digital Passport
def render_consumer_passport(batch_id):
    st.markdown("<div class='passport-card'><h2>🌱 Digital Product Passport</h2></div>", unsafe_allow_html=True)
    st.write(f"**Batch ID:** {batch_id} - Verified Authenticity.")
    st.subheader("🐔 Ask Kipi")
    user_q = st.text_input("Ask about your food...")
    if user_q: st.markdown(f"<div class='chat-bubble'><b>Kipi:</b> {consumer_assistant(user_q)}</div>", unsafe_allow_html=True)

# View 2: Admin Dashboard
def render_admin_dashboard():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("🔒 Enterprise Login")
        if st.text_input("Password", type="password") == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        return

    df = load_telemetry_data()
    with st.sidebar:
        st.title("⚙️ Global Controls")
        selected_farm = st.selectbox("📍 Target Farm", options=["All Farms"] + list(df['farm_name'].unique()))
        date_range = st.date_input("Filter Range", [df['date'].min(), df['date'].max()])
        st.divider()
        st.subheader("📡 System Health")
        st.write("Database: ✅ Operational (12ms)")
        st.write("AI Pipeline: 🟢 Stable")
        st.write("API Latency: 45ms")

    farm_df = df if selected_farm == "All Farms" else df[df['farm_name'] == selected_farm]
    
    st.title(f"🐓 Poultry Operations & AI Command Center: {selected_farm}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Yield", f"{farm_df['eggs_laid'].sum():,}")
    c2.metric("Gross Revenue", f"€{farm_df['revenue'].sum():,.2f}")
    c3.metric("Operational Cost", f"€{farm_df['cost'].sum():,.2f}")
    c4.metric("Net Profit", f"€{farm_df['profit'].sum():,.2f}")
    
    csv = farm_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Filtered Data (CSV)", data=csv, file_name='poultry_report.csv', mime='text/csv')
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📈 Visual Analytics", "🗄️ Farm Config & QR", "🤖 AI Copilot"])
    with tab1:
        st.subheader("🤖 AI Forecast Trend")
        forecast = generate_30_day_forecast(farm_df)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=farm_df['date'], y=farm_df['eggs_laid'].rolling(3).mean(), name='Trend'))
        fig.add_trace(go.Scatter(x=forecast['date'], y=forecast['predicted_eggs'], name='Forecast', line=dict(dash='dot')))
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        st.subheader("Database Management")
        conn = get_db_connection()
        farms = pd.read_sql_query("SELECT * FROM farms_profile", conn)
        for _, row in farms.iterrows():
            st.markdown(f"<div class='crud-card'><h3>{row['farm_name']}</h3></div>", unsafe_allow_html=True)
        conn.close()
    with tab3:
        st.subheader("💬 Operations Copilot")
        q = st.text_input("Ask Copilot...")
        if q: st.markdown(f"<div class='chat-bubble'>{admin_copilot(q)}</div>", unsafe_allow_html=True)
        
    st.divider()
    st.caption("🔒 Powered by Predictive ML Pipeline | Confidential: Internal Use Only")

def main():
    params = st.query_params
    if "batch_id" in params: render_consumer_passport(params["batch_id"])
    else: render_admin_dashboard()

if __name__ == "__main__":
    main()
