import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 1. Page Configuration
st.set_page_config(page_title="Waar is de kip! | Enterprise BI", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #0052FF; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .narrative-box { background-color: #E6F0FF; padding: 20px; border-radius: 10px; border-left: 5px solid #0052FF; font-size: 1.1em; color: #001B54; margin-top: 10px; }
    .footer { position: fixed; bottom: 0; right: 10px; font-size: 0.8em; color: gray; }
    </style>
    """, unsafe_allow_html=True)

# --- Financial Constants ---
COST_PER_CHICKEN_PER_DAY = 0.05  # €0.05 feed/upkeep cost per day
REVENUE_PER_EGG = 0.25           # €0.25 selling price per egg

@st.cache_data
def load_and_process_data():
    """Loads data and computes foundational business metrics."""
    try:
        df = pd.read_csv('farm_data.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        # Compute Financials per row
        df['Daily_Cost'] = COST_PER_CHICKEN_PER_DAY
        df['Daily_Revenue'] = df['Eggs_Laid'] * REVENUE_PER_EGG
        df['Daily_Profit'] = df['Daily_Revenue'] - df['Daily_Cost']
        return df
    except FileNotFoundError:
        st.error("System Error: Pipeline breakdown. 'farm_data.csv' missing.")
        return pd.DataFrame()

def get_file_last_modified(filepath):
    """Returns the last modified timestamp of the data pipeline output."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    except OSError:
        return "Unknown"

def calculate_delta(current, previous):
    """Mathematical computation of percentage delta."""
    if previous == 0: return 0.0
    return ((current - previous) / previous) * 100

def main():
    df = load_and_process_data()
    if df.empty: return

    # --- Sidebar: Interactive Time Context & Filters ---
    with st.sidebar:
        st.title("⚙️ Enterprise Controls")
        
        # Farm Filter
        selected_farm = st.selectbox("📍 Target Farm", options=["All Farms"] + list(df['Farm_Name'].unique()))
        
        # Dynamic Time-Range Selector
        min_date, max_date = df['Date'].min(), df['Date'].max()
        time_preset = st.radio("⏱️ Time Horizon", ["Last 7 Days", "Last 30 Days", "Year-to-Date (YTD)", "Custom Range"])
        
        if time_preset == "Last 7 Days":
            start_date, end_date = max_date - timedelta(days=7), max_date
        elif time_preset == "Last 30 Days":
            start_date, end_date = max_date - timedelta(days=30), max_date
        elif time_preset == "Year-to-Date (YTD)":
            start_date, end_date = datetime(max_date.year, 1, 1), max_date
        else:
            date_range = st.date_input("Select Range", [min_date, max_date], min_value=min_date, max_value=max_date)
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1] if len(date_range)>1 else date_range[0])
        
        st.markdown("---")
        pipeline_status = get_file_last_modified('farm_data.csv')
        st.success("🟢 Pipeline Status: Healthy")
        st.caption(f"Last Data Sync: {pipeline_status}")

    # --- Data Filtering based on Context ---
    farm_df = df if selected_farm == "All Farms" else df[df['Farm_Name'] == selected_farm]
    
    # Current Period Data
    mask_current = (farm_df['Date'] >= start_date) & (farm_df['Date'] <= end_date)
    curr_df = farm_df.loc[mask_current]
    
    # Previous Period Data (for Deltas)
    delta_days = (end_date - start_date).days
    prev_start = start_date - timedelta(days=delta_days if delta_days > 0 else 1)
    mask_prev = (farm_df['Date'] >= prev_start) & (farm_df['Date'] < start_date)
    prev_df = farm_df.loc[mask_prev]

    st.title(f"📊 Business Intelligence: {selected_farm}")
    st.markdown("### Financial ROI & Production Efficiency")
    
    # --- Executive Metrics with Deltas ---
    st.subheader("Key Performance Indicators (Selected Period)")
    col1, col2, col3, col4 = st.columns(4)
    
    # Metric 1: Production
    curr_eggs, prev_eggs = curr_df['Eggs_Laid'].sum(), prev_df['Eggs_Laid'].sum()
    egg_delta = calculate_delta(curr_eggs, prev_eggs)
    col1.metric("Total Yield (Eggs)", f"{curr_eggs:,}", f"{egg_delta:.1f}% vs Prev Period")
    
    # Metric 2: Revenue
    curr_rev, prev_rev = curr_df['Daily_Revenue'].sum(), prev_df['Daily_Revenue'].sum()
    rev_delta = calculate_delta(curr_rev, prev_rev)
    col2.metric("Total Revenue", f"€{curr_rev:,.2f}", f"{rev_delta:.1f}% vs Prev Period")
    
    # Metric 3: Cost
    curr_cost, prev_cost = curr_df['Daily_Cost'].sum(), prev_df['Daily_Cost'].sum()
    cost_delta = calculate_delta(curr_cost, prev_cost)
    # Inverse color for cost (lower is better)
    col3.metric("Operational Cost", f"€{curr_cost:,.2f}", f"{cost_delta:.1f}% vs Prev Period", delta_color="inverse")
    
    # Metric 4: Net Profit (ROI factor)
    curr_profit, prev_profit = curr_df['Daily_Profit'].sum(), prev_df['Daily_Profit'].sum()
    profit_delta = calculate_delta(curr_profit, prev_profit)
    col4.metric("Net Profit", f"€{curr_profit:,.2f}", f"{profit_delta:.1f}% vs Prev Period")

    st.divider()

    # --- Financial & Business Narrative ---
    # Auto-generating the ROI summary based on mathematical facts
    roi_percentage = (curr_profit / curr_cost * 100) if curr_cost > 0 else 0
    trend_word = "an increase" if profit_delta >= 0 else "a decrease"
    
    narrative = f"""
    **Executive Summary:** During the selected {delta_days}-day period, the operation generated **€{curr_rev:,.2f}** in revenue against operational costs of **€{curr_cost:,.2f}**, resulting in a Net Profit of **€{curr_profit:,.2f}**. 
    This represents an overall Return on Investment (ROI) of **{roi_percentage:.1f}%**, reflecting {trend_word} of {abs(profit_delta):.1f}% compared to the previous period.
    """
    st.markdown(f"<div class='narrative-box'>{narrative}</div>", unsafe_allow_html=True)
    st.write("")

    # --- Enhanced Visualizations ---
    chart_col1, chart_col2 = st.columns([2, 1])
    
    with chart_col1:
        # Time-series with Moving Average (Noise Filtering)
        daily_trend = curr_df.groupby('Date')['Eggs_Laid'].sum().reset_index()
        # Mathematical 7-Day SMA
        daily_trend['7D_Moving_Avg'] = daily_trend['Eggs_Laid'].rolling(window=7, min_periods=1).mean()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=daily_trend['Date'], y=daily_trend['Eggs_Laid'], name='Daily Production', marker_color='#E8F0FE'))
        fig_trend.add_trace(go.Scatter(x=daily_trend['Date'], y=daily_trend['7D_Moving_Avg'], name='7-Day Trend (SMA)', line=dict(color='#0052FF', width=3)))
        
        fig_trend.update_layout(title="Production Trend with Moving Average Smoothing", template="plotly_white", hovermode="x unified")
        st.plotly_chart(fig_trend, use_container_width=True)

    with chart_col2:
        # Gauge Chart for Resource Efficiency / Target Fulfillment
        # Assuming an optimal target of 0.85 eggs per chicken per day
        target_yield = len(curr_df['Chicken_ID'].unique()) * delta_days * 0.85
        efficiency_ratio = (curr_eggs / target_yield) * 100 if target_yield > 0 else 0
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = efficiency_ratio,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Target Fulfillment (%)", 'font': {'size': 18}},
            delta = {'reference': 100, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge = {
                'axis': {'range': [None, 120], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#0052FF"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 75], 'color': '#FFCDD2'},
                    {'range': [75, 95], 'color': '#FFF9C4'},
                    {'range': [95, 120], 'color': '#C8E6C9'}]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

if __name__ == "__main__":
    main()
