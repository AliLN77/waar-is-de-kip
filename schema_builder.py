import sqlite3
import uuid
from datetime import datetime, timedelta
import random

def build_enterprise_schema():
    conn = sqlite3.connect("enterprise_poultry.db")
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        farm_id TEXT
    )""")

    # 2. Farms Profile (CRUD Target)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farms_profile (
        farm_id TEXT PRIMARY KEY,
        farm_name TEXT UNIQUE NOT NULL,
        ovr_feed_cost DECIMAL(5,2) NOT NULL,
        heating_type TEXT NOT NULL,
        optimal_breed TEXT NOT NULL
    )""")

    # 3. Livestock Batches (QR Passport Core)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS livestock_batches (
        batch_id TEXT PRIMARY KEY,
        farm_id TEXT NOT NULL,
        breed TEXT NOT NULL,
        hatch_date TEXT NOT NULL,
        diet_type TEXT NOT NULL,
        welfare_std TEXT NOT NULL,
        FOREIGN KEY (farm_id) REFERENCES farms_profile(farm_id)
    )""")

    # 4. Daily Telemetry (Time-Series for ML)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_telemetry (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT NOT NULL,
        date TEXT NOT NULL,
        age_days INTEGER NOT NULL,
        eggs_laid INTEGER NOT NULL,
        mortality INTEGER NOT NULL,
        barn_temp_c DECIMAL(4,1) NOT NULL,
        FOREIGN KEY (batch_id) REFERENCES livestock_batches(batch_id)
    )""")

    # --- Seeding Initial Data ---
    cursor.execute("SELECT COUNT(*) FROM farms_profile")
    if cursor.fetchone()[0] == 0:
        farms = [
            (str(uuid.uuid4()), 'Lommel Hoeve', 0.05, 'Lucht-Lucht Heatpump', 'Sussex'),
            (str(uuid.uuid4()), 'Geel Pluimvee', 0.04, 'Gas Boiler', 'Leghorn'),
            (str(uuid.uuid4()), 'Hasselt Kip', 0.06, 'Lucht-Water Heatpump', 'Rhode Island Red')
        ]
        cursor.executemany("INSERT INTO farms_profile VALUES (?,?,?,?,?)", farms)
        
        # Seed 1 Batch for Lommel
        lommel_id = farms[0][0]
        batch_id = f"BATCH-LOM-{datetime.now().strftime('%Y%m')}-01"
        cursor.execute("INSERT INTO livestock_batches VALUES (?,?,?,?,?,?)",
                       (batch_id, lommel_id, 'Sussex', '2026-01-15', '100% Organic Non-GMO Corn', 'Free Range Class A+'))
        
        # Seed 30 days of telemetry
        start_date = datetime.now() - timedelta(days=30)
        telemetry = []
        for d in range(30):
            curr = start_date + timedelta(days=d)
            temp = round(random.uniform(18.0, 23.0), 1)
            telemetry.append((batch_id, curr.strftime('%Y-%m-%d'), 150+d, random.randint(400, 440), random.randint(0, 2), temp))
        
        cursor.executemany("INSERT INTO daily_telemetry (batch_id, date, age_days, eggs_laid, mortality, barn_temp_c) VALUES (?,?,?,?,?,?)", telemetry)

    conn.commit()
    conn.close()
    print("🟢 Enterprise Database 'enterprise_poultry.db' built and seeded successfully.")

if __name__ == "__main__":
    build_enterprise_schema()