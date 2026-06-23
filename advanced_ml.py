import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

def generate_30_day_forecast(df):
    """
    Predictive AI: Uses Gradient Boosting to forecast the next 30 days of egg production
    based on historical trends and age degradation.
    """
    if df.empty or len(df) < 10:
        return pd.DataFrame()

    features = ['age_days', 'barn_temp_c']
    X = df[features]
    y = df['eggs_laid']

    # Train model
    model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Simulate next 30 days
    last_row = df.iloc[-1]
    future_dates = pd.date_range(start=pd.to_datetime(last_row['date']) + pd.Timedelta(days=1), periods=30)
    
    future_data = []
    current_age = last_row['age_days']
    
    for i in range(30):
        current_age += 1
        # Simulating a slight weather drop for prescriptive demonstration
        simulated_temp = last_row['barn_temp_c'] - (0.1 * i) 
        future_data.append({'date': future_dates[i], 'age_days': current_age, 'barn_temp_c': simulated_temp})
        
    future_df = pd.DataFrame(future_data)
    future_df['predicted_eggs'] = model.predict(future_df[['age_days', 'barn_temp_c']])
    
    return future_df

def generate_prescriptive_insights(farm_name, current_temp, forecast_df):
    """
    Prescriptive AI: Analyzes the forecast and current conditions to prescribe operational actions.
    """
    insights = []
    
    # Rule 1: Temperature Drop Warning
    if forecast_df['barn_temp_c'].min() < 18.0:
        insights.append(f"🚨 **Action Required:** Forecast indicates barn temperatures dropping below 18°C next week. Increase heating in {farm_name} to prevent a 5% yield loss.")
        
    # Rule 2: Age Degradation
    if forecast_df['age_days'].max() > 250:
        insights.append("💡 **Strategic Advisor:** The flock is exceeding 250 days of age. Consider planning a batch rotation within the next 45 days to maintain optimal ROI.")
        
    if not insights:
        insights.append("✅ Operations are optimal. No critical interventions prescribed at this time.")
        
    return insights