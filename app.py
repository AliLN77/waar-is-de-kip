import streamlit as st
import sqlite3
import pandas as pd
# ... بقیه import ها ...
from advanced_ml import generate_30_day_forecast, generate_prescriptive_insights

# 1. Page Configuration
st.set_page_config(page_title="Waar is de kip! | Enterprise", layout="wide", page_icon="🐓")

# 2. اینجا دقیقاً همان جایی است که باید استایل‌دهی را قرار دهی!
st.markdown("""
    <style>
    .main { background-color: #F4F6F9; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #0f172a; }
    .crud-card { background-color: #FFFFFF; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-top: 4px solid #3b82f6; }
    .chart-container { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stApp { max-width: 1400px; margin: 0 auto; }
    </style>
    """, unsafe_allow_html=True)

# 3. بقیه کدهای منطقی برنامه و توابع (مثل load_telemetry_data و غیره)
# ...
COST_PER_CHICKEN = 0.05
REVENUE_PER_EGG = 0.25

def get_db_connection():
    conn = sqlite3.connect('enterprise_poultry.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@st.cache_data
def load_telemetry_data():
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT dt.*, fp.farm_name, lb.breed 
        FROM daily_telemetry dt
        JOIN livestock_batches lb ON dt.batch_id = lb.batch_id
        JOIN farms_profile fp ON lb.farm_id = fp.farm_id
    """, conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['revenue'] = df['eggs_laid'] * REVENUE_PER_EGG
        df['cost'] = COST_PER_CHICKEN * 500 
        df['profit'] = df['revenue'] - df['cost']
    return df

# --- Dual Chatbot Logic ---
def admin_copilot(query):
    q = query.lower()
    if "yield" in q or "drop" in q: return "SQL Insight: Yield variance correlates strongly with temperature drops below 19°C. Adjust HVAC."
    if "breed" in q: return "Leghorn maximizes ROI in Geel (gas boiler), while Sussex is hardier for Lommel's Lucht-Lucht system."
    return "I am your Operational Copilot. Ask about operations, yields, or HVAC optimizations."

def consumer_assistant(query):
    q = query.lower()
    if "diet" in q or "food" in q: return "These chickens are fed a 100% Organic, Non-GMO Corn diet!"
    if "free" in q or "range" in q: return "Yes! They enjoy a Free Range Class A+ lifestyle."
    return "Hi! I'm Kipi 🐔. Ask me about animal welfare, diet, or farm origin."

# --- View 1: Digital Passport (For Mobile QR) ---
def render_consumer_passport(batch_id):
    conn = get_db_connection()
    batch = conn.execute("SELECT * FROM livestock_batches JOIN farms_profile ON livestock_batches.farm_id = farms_profile.farm_id WHERE batch_id = ?", (batch_id,)).fetchone()
    conn.close()
    if not batch:
        st.error("Invalid Batch ID.")
        return

    st.markdown("<div class='passport-card'><h2>🌱 Digital Product Passport</h2><p>Verified Origin & Traceability</p></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.image("https://cdn-icons-png.flaticon.com/512/3014/3014420.png", width=150)
    with col2:
        st.write(f"**Origin:** {batch['farm_name']}")
        st.write(f"**Breed:** {batch['breed']}")
        st.write(f"**Diet:** {batch['diet_type']}")
        st.write(f"**Welfare:** {batch['welfare_std']}")

    st.divider()
    st.subheader("🐔 Ask Kipi (Consumer Assistant)")
    user_q = st.text_input("Ask about your food...")
    if user_q: st.markdown(f"<div class='chat-bubble' style='border-color: #22c55e; background-color: #f0fdf4;'><b>Kipi:</b> {consumer_assistant(user_q)}</div>", unsafe_allow_html=True)

# --- View 2: Enterprise Admin Dashboard ---
def render_admin_dashboard():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("🔒 Enterprise Login")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if pwd == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Invalid Credentials")
        return

    df = load_telemetry_data()
    if df.empty:
        st.error("Database empty. Please run schema_builder.py.")
        return

    # Global Filters in Sidebar
    with st.sidebar:
        st.title("⚙️ Global Controls")
        selected_farm = st.selectbox("📍 Target Farm", options=["All Farms"] + list(df['farm_name'].unique()))
        min_d, max_d = df['date'].min(), df['date'].max()
        date_range = st.date_input("Filter Range", [min_d, max_d], min_value=min_d, max_value=max_d)
        st.success("🟢 AI Engine: Active")

    farm_df = df if selected_farm == "All Farms" else df[df['farm_name'] == selected_farm]
    if len(date_range) == 2:
        farm_df = farm_df[(farm_df['date'] >= pd.to_datetime(date_range[0])) & (farm_df['date'] <= pd.to_datetime(date_range[1]))]

    st.title(f"🐓 Enterprise BI: {selected_farm}")
    
    # Executive KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Yield (Eggs)", f"{farm_df['eggs_laid'].sum():,}")
    c2.metric("Gross Revenue", f"€{farm_df['revenue'].sum():,.2f}")
    c3.metric("Operational Cost", f"€{farm_df['cost'].sum():,.2f}")
    c4.metric("Net Profit (ROI)", f"€{farm_df['profit'].sum():,.2f}")
    st.divider()

    # The 3 Enterprise Tabs
    tab_dash, tab_crud, tab_ai = st.tabs(["📈 Visual Analytics", "🗄️ Farm Config & QR Codes", "🤖 AI Copilot"])

    with tab_dash:
        row1_col1, row1_col2 = st.columns([2, 1])
        with row1_col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🤖 30-Day AI Forecast with Confidence Intervals")
            forecast_df = generate_30_day_forecast(farm_df)
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(x=farm_df['date'], y=farm_df['eggs_laid'], name='Historical', line=dict(color='#0f172a')))
            if not forecast_df.empty:
                fig_fc.add_trace(go.Scatter(
                    x=pd.concat([forecast_df['date'], forecast_df['date'][::-1]]),
                    y=pd.concat([forecast_df['upper_bound'], forecast_df['lower_bound'][::-1]]),
                    fill='toself', fillcolor='rgba(59, 130, 246, 0.2)', line=dict(color='rgba(255,255,255,0)'), name='95% CI'
                ))
                fig_fc.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['predicted_eggs'], name='AI Prediction', line=dict(color='#3b82f6', dash='dot')))
            fig_fc.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_fc, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with row1_col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🧬 Breed Distribution")
            breed_dist = farm_df.groupby('breed')['eggs_laid'].sum().reset_index()
            fig_donut = px.pie(breed_dist, names='breed', values='eggs_laid', hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_donut.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        row2_col1, row2_col2 = st.columns([1, 2])
        with row2_col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🧠 Prescriptive Actions")
            insights = generate_prescriptive_insights(selected_farm, farm_df.iloc[-1]['barn_temp_c'] if not farm_df.empty else 20, forecast_df)
            for insight in insights: st.info(insight)
            st.markdown("</div>", unsafe_allow_html=True)

        with row2_col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🔥 Production Heatmap")
            fig_heat = px.density_heatmap(farm_df, x="age_days", y="barn_temp_c", z="eggs_laid", histfunc="avg", color_continuous_scale="Viridis")
            fig_heat.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_heat, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_crud:
        st.subheader("Farm Database & Cost Overrides")
        conn = get_db_connection()
        farms = pd.read_sql_query("SELECT * FROM farms_profile", conn)
        crud_cols = st.columns(3)
        for idx, row in farms.iterrows():
            with crud_cols[idx % 3]:
                st.markdown(f"<div class='crud-card'><h3>🏢 {row['farm_name']}</h3><p><b>Breed:</b> {row['optimal_breed']}</p><p><b>HVAC:</b> {row['heating_type']}</p></div>", unsafe_allow_html=True)
                with st.form(key=f"form_{row['farm_id']}"):
                    new_cost = st.number_input("Feed Cost (€)", value=float(row['ovr_feed_cost']), step=0.01)
                    if st.form_submit_button("Update DB"):
                        cur = conn.cursor()
                        cur.execute("UPDATE farms_profile SET ovr_feed_cost = ? WHERE farm_id = ?", (new_cost, row['farm_id']))
                        conn.commit()
                        st.success("Updated!")
                        st.rerun()
        
        st.divider()
        st.subheader("📱 Supply Chain: Generate Traceability QR Code")
        batches = pd.read_sql_query("SELECT batch_id, farm_id FROM livestock_batches", conn)
        if not batches.empty:
            selected_batch = st.selectbox("Select Production Batch to Generate Label", batches['batch_id'])
            app_url = "https://waar-is-de-kip.streamlit.app/" 
            passport_link = f"{app_url}?batch_id={selected_batch}"
            
            qr = qrcode.QRCode(version=1, box_size=5, border=2)
            qr.add_data(passport_link)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            
            col_qr1, col_qr2 = st.columns([1, 3])
            with col_qr1: st.image(buf.getvalue(), caption="Ready for Print")
            with col_qr2: 
                st.write("**Digital Passport Link:**")
                st.code(passport_link, language="html")
        conn.close()

    with tab_ai:
        st.subheader("💬 Operations Copilot (RAG Interface)")
        st.warning("🔒 Copilot has access to internal SQL logs, financial models, and HVAC telemetry.")
        admin_q = st.text_input("Ask Copilot...", placeholder="How can I optimize heating in Lommel?")
        if admin_q: st.markdown(f"<div class='chat-bubble'><b>Copilot:</b> {admin_copilot(admin_q)}</div>", unsafe_allow_html=True)

def main():
    query_params = st.query_params
    if "batch_id" in query_params:
        render_consumer_passport(query_params["batch_id"])
    else:
        render_admin_dashboard()

if __name__ == "__main__":
    main()
