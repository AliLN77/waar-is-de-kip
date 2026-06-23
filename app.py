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

# Global UI/UX Styling for High Data Density
st.markdown("""
    <style>
    .main { background-color: #F4F6F9; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #0f172a; }
    .crud-card { background-color: #FFFFFF; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-top: 4px solid #3b82f6; }
    .chart-container { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    /* Reduce top padding */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Database & Cost Constants ---
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
        df['cost'] = COST_PER_CHICKEN * 500 # Approx 500 chickens per batch for calculation
        df['profit'] = df['revenue'] - df['cost']
    return df

# --- Main App ---
def main():
    # Simple Auth
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("🔒 Enterprise Login")
        if st.button("Login (Bypass)"): 
            st.session_state.logged_in = True
            st.rerun()
        return

    df = load_telemetry_data()
    if df.empty:
        st.error("Telemetry data unavailable. Run schema builder.")
        return

    # --- Restore Sidebar Filters ---
    with st.sidebar:
        st.title("⚙️ Global Controls")
        selected_farm = st.selectbox("📍 Target Farm", options=["All Farms"] + list(df['farm_name'].unique()))
        
        st.markdown("---")
        st.markdown("📅 **Time Horizon**")
        min_d, max_d = df['date'].min(), df['date'].max()
        date_range = st.date_input("Filter Range", [min_d, max_d], min_value=min_d, max_value=max_d)
        
        st.markdown("---")
        st.success("🟢 AI Engine: Active")

    # Apply Filters
    farm_df = df if selected_farm == "All Farms" else df[df['farm_name'] == selected_farm]
    if len(date_range) == 2:
        farm_df = farm_df[(farm_df['date'] >= pd.to_datetime(date_range[0])) & (farm_df['date'] <= pd.to_datetime(date_range[1]))]

    st.title("🐓 Enterprise BI: Production & Analytics")
    
    # --- Top Level KPIs (Data Density Restored) ---
    col1, col2, col3, col4 = st.columns(4)
    total_yield = farm_df['eggs_laid'].sum()
    total_rev = farm_df['revenue'].sum()
    total_cost = farm_df['cost'].sum()
    net_profit = farm_df['profit'].sum()
    
    col1.metric("Total Yield (Eggs)", f"{total_yield:,}")
    col2.metric("Gross Revenue", f"€{total_rev:,.2f}")
    col3.metric("Operational Cost", f"€{total_cost:,.2f}")
    col4.metric("Net Profit (ROI)", f"€{net_profit:,.2f}", f"{(net_profit/total_cost*100):.1f}% Margin")
    st.divider()

    tab_dash, tab_crud = st.tabs(["📈 Visual Analytics & Forecast", "🗄️ Farm Configuration (CRUD)"])

    with tab_dash:
        # --- High-Density Grid Layout ---
        row1_col1, row1_col2 = st.columns([2, 1])
        
        with row1_col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🤖 30-Day AI Forecast with Confidence Intervals")
            forecast_df = generate_30_day_forecast(farm_df)
            
            fig_fc = go.Figure()
            # Historical
            fig_fc.add_trace(go.Scatter(x=farm_df['date'], y=farm_df['eggs_laid'], name='Historical', line=dict(color='#0f172a', width=2)))
            
            if not forecast_df.empty:
                # Confidence Interval Shading
                fig_fc.add_trace(go.Scatter(
                    x=pd.concat([forecast_df['date'], forecast_df['date'][::-1]]),
                    y=pd.concat([forecast_df['upper_bound'], forecast_df['lower_bound'][::-1]]),
                    fill='toself', fillcolor='rgba(59, 130, 246, 0.2)', line=dict(color='rgba(255,255,255,0)'),
                    hoverinfo="skip", showlegend=True, name='95% Confidence Interval'
                ))
                # Forecast Line
                fig_fc.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['predicted_eggs'], name='AI Prediction', line=dict(color='#3b82f6', width=3, dash='dot')))
            
            fig_fc.update_layout(template="plotly_white", hovermode="x unified", height=400, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_fc, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with row1_col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🧬 Breed Distribution")
            breed_dist = farm_df.groupby('breed')['eggs_laid'].sum().reset_index()
            fig_donut = px.pie(breed_dist, names='breed', values='eggs_laid', hole=0.6, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_donut.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.write("") # Spacer
        
        row2_col1, row2_col2 = st.columns([1, 2])
        
        with row2_col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🧠 Prescriptive Actions")
            insights = generate_prescriptive_insights(selected_farm, farm_df.iloc[-1]['barn_temp_c'] if not farm_df.empty else 20, forecast_df)
            for insight in insights:
                st.info(insight)
            st.markdown("</div>", unsafe_allow_html=True)

        with row2_col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("🔥 Production Heatmap (Efficiency by Temp/Age)")
            # Adding Heatmap for Data Density
            fig_heat = px.density_heatmap(farm_df, x="age_days", y="barn_temp_c", z="eggs_laid", histfunc="avg", color_continuous_scale="Viridis")
            fig_heat.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_heat, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_crud:
        st.subheader("🗄️ Database Management & Fleet Settings")
        conn = get_db_connection()
        farms = pd.read_sql_query("SELECT * FROM farms_profile", conn)
        
        # Visually appealing CRUD Cards instead of raw dataframes
        crud_cols = st.columns(3)
        for idx, row in farms.iterrows():
            with crud_cols[idx % 3]:
                st.markdown(f"""
                <div class='crud-card'>
                    <h3>🏢 {row['farm_name']}</h3>
                    <p><b>Current Breed:</b> {row['optimal_breed']}</p>
                    <p><b>HVAC System:</b> {row['heating_type']}</p>
                    <p><b>Feed Cost:</b> €{row['ovr_feed_cost']:.2f} / day</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Streamlit Form for Data Integrity
                with st.form(key=f"form_{row['farm_id']}"):
                    new_cost = st.number_input("Update Feed Cost (€)", min_value=0.01, max_value=5.00, value=float(row['ovr_feed_cost']), step=0.01)
                    if st.form_submit_button("💾 Save to DB"):
                        cur = conn.cursor()
                        cur.execute("UPDATE farms_profile SET ovr_feed_cost = ? WHERE farm_id = ?", (new_cost, row['farm_id']))
                        conn.commit()
                        st.success("Database Updated! Refreshing...")
                        st.rerun()
        conn.close()

if __name__ == "__main__":
    main()
