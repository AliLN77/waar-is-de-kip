import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ml_predictor import train_and_predict_eggs

# 1. Page Configuration & Professional Theming
st.set_page_config(
    page_title="Waar is de kip! | Enterprise Dashboard", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="expanded"
)

# Injecting Custom CSS for a Classic Dark/Executive UI
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    h1, h2, h3 { color: #F0F2F6; font-family: 'Helvetica Neue', sans-serif; }
    .stMetric { background-color: #262730; padding: 15px; border-radius: 5px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """
    Loads data and applies mathematical Z-score logic for anomaly detection.
    """
    try:
        df = pd.read_csv('farm_data.csv')
        # Mathematical Intuition: Z-score for environmental monitoring
        mean_temp = df['Barn_Temp_C'].mean()
        std_temp = df['Barn_Temp_C'].std()
        df['Temp_Z_Score'] = (df['Barn_Temp_C'] - mean_temp) / std_temp
        
        # Flagging critical anomalies where |Z| > 3
        df['Is_Anomaly'] = np.where(np.abs(df['Temp_Z_Score']) > 3, True, False)
        return df
    except FileNotFoundError:
        st.error("System Error: 'farm_data.csv' missing. Execute data pipeline first.")
        return pd.DataFrame()

def main():
    """Renders the Enterprise-grade Streamlit Dashboard."""
    
    # Sidebar Navigation & Filters
    with st.sidebar:
        st.title("Admin Controls")
        st.markdown("Use filters to analyze specific subsets of the farm.")
        
        df = load_and_process_data()
        if df.empty:
            return
            
        selected_breed = st.multiselect("Filter by Breed", options=df['Breed'].unique(), default=df['Breed'].unique())
        
        st.markdown("---")
        st.markdown("**System Status:** :green[Online]")
        st.markdown("**Cloud Environment:** Production")

    # Dynamic Data Filtering
    filtered_df = df[df['Breed'].isin(selected_breed)]

    # Header Section
    st.title("Waar is de kip! 🚀")
    st.markdown("### Next-Generation Supply Chain Traceability & Predictive AI")
    st.divider()

    # Integrating Machine Learning Pipeline
    model, ml_report = train_and_predict_eggs('farm_data.csv')

    # Executive KPI Row (Business Value Representation)
    st.subheader("Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Active Livestock", value=f"{filtered_df['Chicken_ID'].nunique():,}")
    with col2:
        current_avg_eggs = round(filtered_df['Eggs_Laid'].mean(), 2)
        st.metric(label="Avg Daily Production", value=current_avg_eggs, delta="0.1% vs Last Week")
    with col3:
        # AI Forecasting Output
        ai_pred = ml_report['predicted_total_eggs_tomorrow'] if model else "N/A"
        st.metric(label="🔮 AI Forecast (Tomorrow)", value=ai_pred, delta="Predicted Increase", delta_color="normal")
    with col4:
        # System Health & Anomaly Status
        anomalies_count = filtered_df['Is_Anomaly'].sum()
        status_color = "normal" if anomalies_count == 0 else "inverse"
        st.metric(label="⚠️ Critical Temp Anomalies", value=anomalies_count, delta="System Alerts", delta_color=status_color)

    st.divider()

    # Advanced Visualizations for Directorate & Stakeholders
    st.subheader("Deep-Dive Analytics & Anomaly Detection")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 3D Multidimensional Plot (Wow Factor)
        fig_3d = px.scatter_3d(
            filtered_df.sample(min(500, len(filtered_df))), 
            x='Age_Days', 
            y='Weight_Kg', 
            z='Eggs_Laid',
            color='Breed',
            title='3D Multidimensional Farm Demographics',
            template='plotly_dark'
        )
        st.plotly_chart(fig_3d, use_container_width=True)

    with chart_col2:
        # Statistical Anomaly Diagnostics
        fig_anomaly = px.scatter(
            filtered_df, 
            x='Date', 
            y='Barn_Temp_C', 
            color='Is_Anomaly',
            color_discrete_map={False: '#00CC96', True: '#EF553B'},
            title='Sensor Diagnostics: Environmental Anomalies',
            template='plotly_dark'
        )
        fig_anomaly.add_hline(y=filtered_df['Barn_Temp_C'].mean(), line_dash="dot", annotation_text="Optimal Mean", annotation_position="bottom right")
        st.plotly_chart(fig_anomaly, use_container_width=True)

    # ITIL Standard: Data Export Capability for Operations
    st.divider()
    st.subheader("Raw Data Export")
    with st.expander("View & Download Tabular Data"):
        st.dataframe(filtered_df.head(100), use_container_width=True)
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Complete Dataset as CSV",
            data=csv,
            file_name='farm_export.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()