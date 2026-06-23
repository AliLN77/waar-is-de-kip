import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

def train_and_predict_eggs(df_path='farm_data.csv'):
    """
    Trains a Linear Regression model to predict egg production 
    based on age, weight, and barn temperature.
    """
    try:
        df = pd.read_csv(df_path)
    except FileNotFoundError:
        return None, "Data file not found. Please generate data first."

    # Feature selection (X) and Target variable (y)
    features = ['Age_Days', 'Weight_Kg', 'Barn_Temp_C']
    X = df[features]
    y = df['Eggs_Laid']

    # Splitting data into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model initialization and training
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Model evaluation (Root Mean Squared Error)
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    # Business Logic: Predict tomorrow's eggs for the whole farm based on latest conditions
    latest_data = df.groupby('Chicken_ID').last().reset_index()
    X_latest = latest_data[features]
    
    # Adding a slight aging effect for tomorrow
    X_latest['Age_Days'] = X_latest['Age_Days'] + 1 
    
    future_predictions = model.predict(X_latest)
    
    # Ensure no negative predictions and round to integers
    total_predicted_eggs = int(np.sum(np.maximum(0, np.round(future_predictions))))

    business_report = {
        "model_rmse": round(rmse, 2),
        "predicted_total_eggs_tomorrow": total_predicted_eggs,
        "active_chickens": len(latest_data)
    }

    return model, business_report

# Example usage
# trained_model, report = train_and_predict_eggs()
# print(report)