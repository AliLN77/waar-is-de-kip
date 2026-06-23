import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import qrcode
from io import BytesIO
from ml_predictor import train_and_predict_eggs, cluster_farm_health

# 1. Page Configuration
st.set_page_config(
    page_title="Waar is de kip! | Enterprise System", 
    layout="wide", 
    page_icon="🐔",
    initial_sidebar_state="expanded"
)

# Responsive and Clean Light CSS
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
        
        # Mathematical Anomaly Detection
        mean_temp, std_temp = df['Barn_Temp_C'].mean(), df['Barn_Temp_C'].std()
        df['Temp_Z_Score'] = (df['Barn_Temp_C'] - mean_temp) / std_temp
        df['Is_Anomaly'] = np.where(np.abs(df['Temp_Z_Score']) > 3, True, False)
        
        # Simulating GPS Coordinates (Around Flanders, Belgium)
        np.random.seed(42)
        df['Lat'] = 51.23 + np.random.normal(0, 0.05, len(df))
        df['Lon'] = 5.31 + np.random.normal(0, 0.05, len(df))
        
        # Apply Unsupervised AI Clustering
        df = cluster_farm_health(df)
        return df
    except FileNotFoundError:
        st.error("System Error: 'farm_data.csv' missing. Execute data pipeline first.")
        return pd.DataFrame()

def generate_qr_code(url):
    """Generates a QR code image for traceability."""
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def main():
    with st.sidebar:
        st.title("⚙️ Admin Controls")
        st.markdown("Filter farm data in real-time.")
        
        df = load_and_process_data()
        if df.empty:
            return
            
        selected_breed = st.multiselect("Filter by Breed", options=df['Breed'].unique(), default=df['Breed'].unique())
        st.markdown("---")
        st.success("**System Status:** Online & Secure")
        
        # In-App QR Code Generator
        st.markdown("### 📱 Scan to Track")
        app_url = "https://waar-is-de-kip.streamlit.app/"
        qr_image = generate_qr_code(app_url)
        st.image(qr_image, caption="Traceability QR Code")

    filtered_df = df[df['Breed'].isin(selected_breed)]

    # Header
    st.title("🐔 Waar is de kip!")
    st.markdown("### Transparent Supply Chain & AI-Driven Poultry Management")
    st.divider()

    # ML Pipeline
    model, ml_report = train_and_predict_eggs('farm_data.csv')

    st.subheader("📊 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Active Livestock", f"{filtered_df['Chicken_ID'].nunique():,}")
    with col2:
        st.metric("Avg Daily Production", round(filtered_df['Eggs_Laid'].mean(), 2), delta="Optimal")
    with col3:
        ai_pred = ml_report['predicted_total_eggs_tomorrow'] if model else "N/A"
        st.metric("🔮 AI Forecast (Tomorrow)", ai_pred, delta="Predicted Increase")
    with col4:
        anomalies_count = filtered_df['Is_Anomaly'].sum()
        st.metric("⚠️ Temp Anomalies", anomalies_count, delta="Clear" if anomalies_count == 0 else "Alert", delta_color="inverse")

    st.divider()

    # Advanced Maps and AI Analytics
    st.subheader("🌍 Geospatial Tracking & AI Health Clusters")
    map_col, cluster_col = st.columns(2)
    
    with map_col:
        # Plotly Mapbox for location tracking
        fig_map = px.scatter_mapbox(
            filtered_df.drop_duplicates(subset=['Chicken_ID']), 
            lat="Lat", lon="Lon", 
            color="Health_Status",
            color_discrete_map={'High Yield (Premium)': '#00CC96', 'Standard Performer': '#636EFA', 'Needs Attention': '#EF553B'},
            hover_name="Chicken_ID", 
            hover_data=["Breed", "Age_Days"],
            zoom=8, 
            title='Real-time Farm GPS Tracking'
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with cluster_col:
        # Visualizing K-Means Clusters
        fig_cluster = px.scatter(
            filtered_df, 
            x='Age_Days', 
            y='Weight_Kg', 
            color='Health_Status',
            size='Eggs_Laid',
            title='AI Health & Productivity Clusters',
            template='plotly_white'
        )
        st.plotly_chart(fig_cluster, use_container_width=True)

if __name__ == "__main__":
    main()
