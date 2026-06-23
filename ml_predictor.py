import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

def train_and_predict_eggs(df_path='farm_data.csv'):
    """Trains a Linear Regression model for forecasting daily production."""
    try:
        df = pd.read_csv(df_path)
    except FileNotFoundError:
        return None, "Data file not found."

    features = ['Age_Days', 'Weight_Kg', 'Barn_Temp_C']
    X = df[features]
    y = df['Eggs_Laid']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    latest_data = df.groupby('Chicken_ID').last().reset_index()
    X_latest = latest_data[features].copy()
    X_latest.loc[:, 'Age_Days'] = X_latest['Age_Days'] + 1 
    
    future_predictions = model.predict(X_latest)
    total_predicted_eggs = int(np.sum(np.maximum(0, np.round(future_predictions))))

    business_report = {
        "model_rmse": round(rmse, 2),
        "predicted_total_eggs_tomorrow": total_predicted_eggs,
        "active_chickens": len(latest_data)
    }
    return model, business_report

def cluster_farm_health(df):
    """
    Applies K-Means Clustering to group chickens into health and productivity categories.
    """
    features = ['Age_Days', 'Weight_Kg', 'Eggs_Laid']
    X = df[features]
    
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster_ID'] = kmeans.fit_predict(X)
    
    cluster_mapping = {
        0: 'Standard Performer',
        1: 'High Yield (Premium)',
        2: 'Needs Attention'
    }
    df['Health_Status'] = df['Cluster_ID'].map(cluster_mapping)
    return df
