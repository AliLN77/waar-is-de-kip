import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_farm_data(num_chickens=500, days=30):
    """
    Generates synthetic farm data mapped to specific discrete farm locations.
    """
    np.random.seed(42)
    
    # Defining distinct farm locations for clear traceability
    farms = [
        {'Farm_Name': 'Lommel Hoeve', 'Lat': 51.230, 'Lon': 5.310},
        {'Farm_Name': 'Geel Pluimvee', 'Lat': 51.160, 'Lon': 4.990},
        {'Farm_Name': 'Hasselt Kip', 'Lat': 50.930, 'Lon': 5.330}
    ]
    
    chicken_ids = [f"KIP-{i:04d}" for i in range(num_chickens)]
    breeds = np.random.choice(['Leghorn', 'Sussex', 'Rhode Island Red'], num_chickens)
    
    # Assigning each chicken to a specific farm permanently
    assigned_farms = np.random.choice(farms, num_chickens)
    
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        temp_noise = np.random.normal(0, 0.5) # Daily temperature variation
        
        for i in range(num_chickens):
            farm = assigned_farms[i]
            age_days = np.random.randint(100, 300) + day 
            weight_kg = np.random.normal(loc=2.5, scale=0.2)
            eggs_laid = np.random.poisson(lam=0.8)
            
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Chicken_ID': chicken_ids[i],
                'Farm_Name': farm['Farm_Name'],
                'Lat': farm['Lat'],
                'Lon': farm['Lon'],
                'Breed': breeds[i],
                'Age_Days': age_days,
                'Weight_Kg': round(weight_kg, 2),
                'Eggs_Laid': eggs_laid,
                'Barn_Temp_C': round(22.0 + temp_noise, 1)
            })
            
    df = pd.DataFrame(data)
    df.to_csv('farm_data.csv', index=False)
    return df

if __name__ == "__main__":
    generate_farm_data()
