import streamlit as st
import sqlite3
import pandas as pd
import qrcode
from io import BytesIO
import urllib.parse
from advanced_ml import generate_30_day_forecast, generate_prescriptive_insights
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Waar is de kip! | Enterprise", layout="wide", page_icon="🐓")

# Custom CSS for UI
st.markdown("""
    <style>
    .passport-card { background-color: #f0fdf4; padding: 20px; border-radius: 15px; border: 2px solid #22c55e; text-align: center; }
    .chat-bot-admin { background-color: #e0f2fe; padding: 15px; border-radius: 10px; border-left: 5px solid #0284c7; }
    .chat-bot-consumer { background-color: #fdf4ff; padding: 15px; border-radius: 10px; border-left: 5px solid #c026d3; }
    </style>
    """, unsafe_allow_html=True)

# --- Database Connection ---
def get_db_connection():
    conn = sqlite3.connect('enterprise_poultry.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# --- AI Chatbot Logic (Dual Persona) ---
def admin_copilot(query):
    query = query.lower()
    if "yield" in query or "drop" in query:
        return "Internal SQL Analysis: The yield drop correlates directly with a 3°C temperature variance recorded last Tuesday. Adjust HVAC parameters."
    if "breed" in query:
        return "Based on historical ROI, 'Leghorn' maximizes profit margins by 12% in the Geel facility during winter."
    return "I am your Operational Copilot. I have access to financial and mortality data. How can I assist?"

def consumer_assistant(query):
    query = query.lower()
    if "free" in query or "range" in query:
        return "Yes! These chickens enjoy a Free Range Class A+ lifestyle, ensuring high animal welfare."
    if "diet" in query or "fed" in query:
        return "They are fed a premium, 100% Organic Non-GMO Corn diet. No artificial hormones are used!"
    if "profit" in query or "cost" in query or "money" in query:
        return "I'm here to answer questions about animal welfare and product quality! I don't have access to business operations data."
    return "Hello! I'm Kipi. Ask me about the origin, diet, and welfare of your food!"

# --- View 1: Consumer Digital Passport (Mobile QR Landing Page) ---
def render_consumer_passport(batch_id):
    conn = get_db_connection()
    batch = conn.execute("SELECT * FROM livestock_batches JOIN farms_profile ON livestock_batches.farm_id = farms_profile.farm_id WHERE batch_id = ?", (batch_id,)).fetchone()
    conn.close()

    if not batch:
        st.error("Invalid Product Batch ID.")
        return

    st.markdown(f"<div class='passport-card'><h2>🌱 Digital Product Passport</h2><p>Verified Origin & Traceability</p></div>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3014/3014420.png", width=150)
    with col2:
        st.markdown(f"**Farm Origin:** {batch['farm_name']}")
        st.markdown(f"**Chicken Breed:** {batch['breed']}")
        st.markdown(f"**Diet Standard:** {batch['diet_type']}")
        st.markdown(f"**Welfare Certification:** {batch['welfare_std']}")
        st.markdown(f"**Hatch Date:** {batch['hatch_date']}")

    st.divider()
    st.subheader("🐔 Consumer Assistant (Ask about this batch)")
    user_q = st.text_input("Ask a question about your food...")
    if user_q:
        st.markdown(f"<div class='chat-bot-consumer'><b>Kipi:</b> {consumer_assistant(user_q)}</div>", unsafe_allow_html=True)

# --- View 2: Internal Admin Dashboard (CRUD, ML, AI) ---
def render_admin_dashboard():
    # Simple Session Auth
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔒 Enterprise Login")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == "admin123": # Hardcoded for demonstration
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
        return

    st.title("⚙️ Enterprise Poultry Management")
    tab_dash, tab_crud, tab_ai = st.tabs(["📈 Predictive Dashboard", "🗄️ Farm Settings (CRUD) & QR", "🤖 Operational Copilot"])
    
    conn = get_db_connection()

    with tab_dash:
        # Load Telemetry
        df = pd.read_sql_query("SELECT * FROM daily_telemetry", conn)
        if not df.empty:
            forecast_df = generate_30_day_forecast(df)
            
            st.subheader("📊 30-Day Production Forecast")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['date'], y=df['eggs_laid'], name='Historical Production', line=dict(color='blue')))
            if not forecast_df.empty:
                fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['predicted_eggs'], name='AI Forecast (Next 30 Days)', line=dict(color='red', dash='dot')))
            
            fig.update_layout(template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("🧠 Prescriptive AI Advisor")
            insights = generate_prescriptive_insights("Lommel Hoeve", df.iloc[-1]['barn_temp_c'], forecast_df)
            for insight in insights:
                st.info(insight)

    with tab_crud:
        st.subheader("Farm Database Operations")
        farms = pd.read_sql_query("SELECT * FROM farms_profile", conn)
        st.dataframe(farms, use_container_width=True)
        
        with st.expander("Update Farm Feed Cost (Update)"):
            target_farm = st.selectbox("Select Farm", farms['farm_name'])
            new_cost = st.number_input("New Feed Cost (€)", min_value=0.01, max_value=5.00, value=0.05)
            if st.button("Update Database"):
                conn.execute("UPDATE farms_profile SET ovr_feed_cost = ? WHERE farm_name = ?", (new_cost, target_farm))
                conn.commit()
                st.success(f"Cost updated for {target_farm}. Refreshing...")
                st.rerun()
                
        st.subheader("📱 Generate Traceability QR Code")
        batches = pd.read_sql_query("SELECT batch_id FROM livestock_batches", conn)
        if not batches.empty:
            selected_batch = st.selectbox("Select Product Batch", batches['batch_id'])
            # Dynamic URL linking back to this app with query parameters
            app_url = "https://waar-is-de-kip.streamlit.app/" # Update with your deployed URL
            passport_link = f"{app_url}?batch_id={selected_batch}"
            
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(passport_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            
            st.image(buf.getvalue(), caption="Print for Product Packaging")
            st.code(passport_link, language="html")

    with tab_ai:
        st.subheader("💬 Operations Copilot (Internal RAG)")
        st.warning("🔒 This bot has access to financial and operational SQL databases.")
        admin_q = st.text_input("Ask Copilot...", placeholder="Why did the yield drop last Tuesday?")
        if admin_q:
            st.markdown(f"<div class='chat-bot-admin'><b>Copilot:</b> {admin_copilot(admin_q)}</div>", unsafe_allow_html=True)

    conn.close()

# --- Main App Router ---
def main():
    # Check if a consumer is scanning a QR code
    query_params = st.query_params
    if "batch_id" in query_params:
        # Render the Mobile Digital Passport
        render_consumer_passport(query_params["batch_id"])
    else:
        # Render the Admin Enterprise Dashboard
        render_admin_dashboard()

if __name__ == "__main__":
    main()
