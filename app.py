import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from ml_predictor import train_and_predict_eggs, cluster_farm_health

# 1. Page Configuration
st.set_page_config(page_title="Waar is de kip! | Intelligence", layout="wide", page_icon="🐓")

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .chat-bubble { background-color: #E8F0FE; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    try:
        df = pd.read_csv('farm_data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        df = cluster_farm_health(df)
        return df
    except FileNotFoundError:
        st.error("System Error: Execute data pipeline first.")
        return pd.DataFrame()

def chatbot_kipi(user_input):
    """Simple rule-based NLP logic for Kipi the Chatbot."""
    input_lower = user_input.lower()
    if "leghorn" in input_lower:
        return "🐔 **Leghorn:** Excellent for Egg production. Adapts well to Geel's moderate climate. Yields 280+ eggs/year."
    elif "sussex" in input_lower:
        return "🐓 **Sussex:** Great dual-purpose (Meat & Egg). Thrives in Lommel's sandy environment. Yields ~250 eggs/year."
    elif "rhode" in input_lower or "red" in input_lower:
        return "🦅 **Rhode Island Red:** Very hardy, excellent for Meat and Eggs. Best for Hasselt's climate."
    elif "meat" in input_lower:
        return "🥩 For meat production, I highly recommend Sussex or Rhode Island Red."
    elif "egg" in input_lower:
        return "🥚 For pure egg production, Leghorn is the absolute champion!"
    else:
        return "Puk Puk! 🐔 I am Kipi. Ask me about chicken breeds (Leghorn, Sussex, Rhode Island), eggs, or meat!"

def main():
    df = load_and_process_data()
    if df.empty: return

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1864/1864470.png", width=80)
        st.title("⚙️ Operations")
        selected_farm = st.selectbox("📍 Select Farm Location", options=["All Farms"] + list(df['Farm_Name'].unique()))
        st.success("**System Status:** Online")

    filtered_df = df if selected_farm == "All Farms" else df[df['Farm_Name'] == selected_farm]

    st.title(f"🐓 Waar is de kip! - {selected_farm}")
    st.markdown("### Next-Gen Poultry Intelligence & Seasonal Analytics")
    
    # UI Organization using Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Performance & Seasonality", "🧬 Breed Intelligence", "🤖 Kipi Chatbot"])

    with tab1:
        st.subheader("Executive Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Active Livestock", f"{filtered_df['Chicken_ID'].nunique():,}")
        with col2: st.metric("Total Eggs Produced", f"{filtered_df['Eggs_Laid'].sum():,}")
        with col3: st.metric("Avg Weight (Kg)", round(filtered_df['Weight_Kg'].mean(), 2))
        with col4: st.metric("Current Farm Temp", f"{round(filtered_df['Barn_Temp_C'].iloc[-1], 1)}°C")

        st.divider()
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Seasonal Analysis Chart
            seasonal_data = filtered_df.groupby([filtered_df['Date'].dt.to_period('M')])['Eggs_Laid'].sum().reset_index()
            seasonal_data['Date'] = seasonal_data['Date'].astype(str)
            fig_season = px.area(seasonal_data, x='Date', y='Eggs_Laid', title="🌦️ Seasonal Production Trends (Peak in Summer)", template="plotly_white")
            st.plotly_chart(fig_season, use_container_width=True)
            
        with chart_col2:
            # Cylindrical/Bar comparison between farms
            farm_perf = df.groupby('Farm_Name')['Eggs_Laid'].sum().reset_index()
            fig_bar = px.bar(farm_perf, x='Farm_Name', y='Eggs_Laid', color='Farm_Name', title="🏭 Farm Efficiency Comparison (Cylindrical)", text_auto='.2s')
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        st.subheader("🧬 Optimal Breed Mapping & Characteristics")
        st.markdown("Compare primary indexes to maximize ROI based on region and purpose.")
        
        # Breed Characteristics Table
        breed_data = {
            "Breed 🐣": ["Leghorn 🐔", "Sussex 🐓", "Rhode Island Red 🦅"],
            "Primary Yield": ["Eggs (High)", "Dual (Meat & Eggs)", "Dual (Heavy Meat)"],
            "Optimal Region": ["Geel", "Lommel", "Hasselt"],
            "Climate Resilience": ["Moderate", "High (Cold Hardy)", "Very High"],
            "Avg Annual Eggs": [280, 250, 260],
            "Avg Market Weight": ["2.5 Kg", "3.2 Kg", "3.9 Kg"]
        }
        st.dataframe(pd.DataFrame(breed_data), use_container_width=True)
        
        st.info("💡 **Strategic Insight:** Rearing Leghorns in Geel increases egg yield by 15% due to optimal climate matching.")

    with tab3:
        st.subheader("🤖 Ask Kipi (AI Assistant)")
        st.markdown("Ask Kipi about breed characteristics, optimal environments, or production types.")
        
        # Simple Custom Chatbot Interface
        user_question = st.text_input("Talk to Kipi...", placeholder="e.g., Which breed is best for meat?")
        if user_question:
            response = chatbot_kipi(user_question)
            st.markdown(f"<div class='chat-bubble'><b>You:</b> {user_question}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chat-bubble' style='background-color: #E6F4EA;'><b>Kipi 🐔:</b> {response}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
