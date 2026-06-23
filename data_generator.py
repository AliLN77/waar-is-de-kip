import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_farm_data(num_chickens=500, days=365):
    """
    Generates 1 year of farm data incorporating seasonal trigonometric logic 
    for accurate egg production forecasting.
    """
    np.random.seed(42)
    
    farms = [
        {'Farm_Name': 'Lommel Hoeve', 'Lat': 51.230, 'Lon': 5.310, 'Optimal_Breed': 'Sussex'},
        {'Farm_Name': 'Geel Pluimvee', 'Lat': 51.160, 'Lon': 4.990, 'Optimal_Breed': 'Leghorn'},
        {'Farm_Name': 'Hasselt Kip', 'Lat': 50.930, 'Lon': 5.330, 'Optimal_Breed': 'Rhode Island Red'}
    ]
    
    chicken_ids = [f"KIP-{i:04d}" for i in range(num_chickens)]
    breeds = np.random.choice(['Leghorn', 'Sussex', 'Rhode Island Red'], num_chickens)
    assigned_farms = np.random.choice(farms, num_chickens)
    
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        day_of_year = current_date.timetuple().tm_yday
        
        # Mathematical Intuition: Seasonal seasonality using Sine wave
        # Peak production in Summer (day ~170), lowest in Winter
        seasonality_factor = 1 + 0.3 * np.sin((2 * np.pi / 365) * day_of_year - (np.pi / 2))
        temp_noise = np.random.normal(0, 1.5)
        seasonal_temp = 15.0 + 10.0 * np.sin((2 * np.pi / 365) * day_of_year - (np.pi / 2)) + temp_noise
        
        for i in range(num_chickens):
            farm = assigned_farms[i]
            age_days = np.random.randint(100, 300) + day 
            weight_kg = np.random.normal(loc=2.5, scale=0.2)
            
            # Base lambda modified by season and breed-farm optimization
            base_lam = 0.8
            if breeds[i] == farm['Optimal_Breed']:
                base_lam += 0.15 # 15% boost if breed matches optimal region
                
            eggs_laid = np.random.poisson(lam=base_lam * seasonality_factor)
            
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Month': current_date.strftime('%B'),
                'Chicken_ID': chicken_ids[i],
                'Farm_Name': farm['Farm_Name'],
                'Lat': farm['Lat'],
                'Lon': farm['Lon'],
                'Breed': breeds[i],
                'Age_Days': age_days,
                'Weight_Kg': round(weight_kg, 2),
                'Eggs_Laid': eggs_laid,
                'Barn_Temp_C': round(seasonal_temp, 1)
            })
            
    df = pd.DataFrame(data)
    df.to_csv('farm_data.csv', index=False)
    return df

if __name__ == "__main__":
    generate_farm_data()
