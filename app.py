import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import qrcode
from io import BytesIO
from ml_predictor import train_and_predict_eggs, cluster_farm_health

st.set_page_config(
    page_title="Waar is de kip! | Enterprise System", 
    layout="wide", 
    page_icon="🐔",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00CC96;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    try:
        df = pd.read_csv('farm_data.csv')
        mean_temp, std_temp = df['Barn_Temp_C'].mean(), df['Barn_Temp_C'].std()
        df['Temp_Z_Score'] = (df['Barn_Temp_C'] - mean_temp) / std_temp
        df['Is_Anomaly'] = np.where(np.abs(df['Temp_Z_Score']) > 3, True, False)
        df = cluster_farm_health(df)
        return df
    except FileNotFoundError:
        st.error("System Error: 'farm_data.csv' missing. Execute data pipeline first.")
        return pd.DataFrame()

def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def main():
    df = load_and_process_data()
    if df.empty: return

    with st.sidebar:
        st.title("⚙️ Farm Controls")
        st.markdown("Isolate data for traceability.")
        
        # New clean filter based on Farm locations
        selected_farm = st.selectbox("📍 Select Farm Location", options=["All Farms"] + list(df['Farm_Name'].unique()))
        selected_breed = st.multiselect("🐔 Filter by Breed", options=df['Breed'].unique(), default=df['Breed'].unique())
        
        st.markdown("---")
        app_url = "https://waar-is-de-kip.streamlit.app/"
        st.image(generate_qr_code(app_url), caption="Traceability QR Code")

    # Applying filters logic
    filtered_df = df[df['Breed'].isin(selected_breed)]
    if selected_farm != "All Farms":
        filtered_df = filtered_df[filtered_df['Farm_Name'] == selected_farm]

    st.title(f"🐔 Waar is de kip! - {selected_farm}")
    st.markdown("### Transparent Supply Chain & AI-Driven Poultry Management")
    st.divider()

    model, ml_report = train_and_predict_eggs('farm_data.csv')

    st.subheader("📊 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Active Livestock", f"{filtered_df['Chicken_ID'].nunique():,}")
    with col2: st.metric("Avg Daily Production", round(filtered_df['Eggs_Laid'].mean(), 2))
    with col3: st.metric("🔮 AI Forecast (Tomorrow)", ml_report['predicted_total_eggs_tomorrow'] if model else "N/A")
    with col4: st.metric("⚠️ Temp Anomalies", filtered_df['Is_Anomaly'].sum())

    st.divider()
    st.subheader("🌍 Regional Tracing & AI Health Clusters")
    
    map_col, cluster_col = st.columns(2)
    
    with map_col:
        # Clean Map: Aggregated by Farm instead of scattered dots
        farm_agg = filtered_df.groupby(['Farm_Name', 'Lat', 'Lon']).size().reset_index(name='Total_Chickens')
        fig_map = px.scatter_mapbox(
            farm_agg, 
            lat="Lat", lon="Lon", 
            color="Farm_Name",
            size="Total_Chickens",
            hover_name="Farm_Name",
            zoom=8, 
            title='Verified Farm Locations'
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with cluster_col:
        fig_cluster = px.scatter(
            filtered_df, 
            x='Age_Days', 
            y='Weight_Kg', 
            color='Health_Status',
            title='Productivity Segments',
            template='plotly_white'
        )
        st.plotly_chart(fig_cluster, use_container_width=True)

if __name__ == "__main__":
    main()
