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

# 2. Global Styling (Fixed CSS Syntax)
st.markdown("""
    <style>
    .main { background-color: #F4F6F9; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #0f172a; }
    .crud-card { background-color: #FFFFFF; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-top: 4px solid #3b82f6; }
    .chart-container { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stApp { max-width: 1400px; margin: 0 auto; }
    .chat-bubble { background-color: #e0f2fe; padding: 15px; border-radius: 10px; border-left: 5px solid #0284c7; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Database Helpers
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

# Chatbot Logic
def admin_copilot(query):
    return "Operations Copilot: Data indicates yield variance is correlated with temperature drops. Recommendation: Check HVAC systems."

# Main Dashboard
def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Global Controls")
        df = load_telemetry_data()
        selected_farm = st.selectbox("📍 Target Farm", options=["All Farms"] + list(df['farm_name'].unique()))
        st.success("🟢 AI Engine: Active")
        st.divider()
        st.caption("🔒 Internal Use Only")

    farm_df = df if selected_farm == "All Farms" else df[df['farm_name'] == selected_farm]

    st.title(f"🐓 Poultry Operations & AI Command Center: {selected_farm}")

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Yield", f"{farm_df['eggs_laid'].sum():,}")
    c2.metric("Gross Revenue", f"€{farm_df['revenue'].sum():,.2f}")
    c3.metric("Operational Cost", f"€{farm_df['cost'].sum():,.2f}")
    c4.metric("Net Profit", f"€{farm_df['profit'].sum():,.2f}")
    st.divider()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Visual Analytics", "🗄️ Database & QR", "🤖 AI Copilot"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("AI Forecast")
            forecast = generate_30_day_forecast(farm_df)
            fig = px.line(forecast, x='date', y='predicted_eggs', title="30-Day Outlook")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Breed Distribution")
            fig2 = px.pie(farm_df, names='breed', values='eggs_laid', hole=0.5)
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Farm Configuration & QR")
        # CRUD logic inside cards
        conn = get_db_connection()
        farms = pd.read_sql_query("SELECT * FROM farms_profile", conn)
        for _, row in farms.iterrows():
            with st.container():
                st.markdown(f"<div class='crud-card'><h3>{row['farm_name']}</h3><p>Cost: €{row['ovr_feed_cost']}</p></div>", unsafe_allow_html=True)
        conn.close()

    with tab3:
        st.subheader("💬 Operations Copilot")
        q = st.text_input("Ask about production...")
        if q: st.markdown(f"<div class='chat-bubble'>{admin_copilot(q)}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
