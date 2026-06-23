import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_farm_data(num_chickens=500, days=30):
    """
    Generates synthetic farm data including temperature, chicken weight, 
    and daily egg production based on statistical distributions.
    """
    np.random.seed(42) # For exact reproducibility
    
    # 1. Chicken IDs and Breeds
    chicken_ids = [f"KIP-{i:04d}" for i in range(num_chickens)]
    breeds = np.random.choice(['Leghorn', 'Sussex', 'Rhode Island Red'], num_chickens)
    
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Simulating Barn Temperature (Mean 22.0C with Gaussian noise)
        temp = np.random.normal(loc=22.0, scale=1.5)
        
        for i in range(num_chickens):
            # Age and Weight based on Normal Distribution
            age_days = np.random.randint(100, 300) + day 
            weight_kg = np.random.normal(loc=2.5, scale=0.2)
            
            # Egg production modeled with Poisson Distribution (Mean 0.8 eggs/day)
            eggs_laid = np.random.poisson(lam=0.8)
            
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Chicken_ID': chicken_ids[i],
                'Breed': breeds[i],
                'Age_Days': age_days,
                'Weight_Kg': round(weight_kg, 2),
                'Eggs_Laid': eggs_laid,
                'Barn_Temp_C': round(temp, 1)
            })
            
    df = pd.DataFrame(data)
    # Save the generated dataset
    df.to_csv('farm_data.csv', index=False)
    return df

if __name__ == "__main__":
    generate_farm_data()