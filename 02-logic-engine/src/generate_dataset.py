import csv
import random
import math
from datetime import datetime, timedelta

# Realistic Locations in Nagpur
LOCATIONS = [
    "GMC_Nagpur",
    "Mayo_Hospital",
    "AIIMS_Nagpur",
    "Lata_Mangeshkar_Hospital",
    "Wockhardt_Hospital"
]

import os

def generate_10k_dataset(filename="../artifacts/synthetic_hospital_data_10k.csv"):
    print(f"Generating 10,000 synthetic records for {filename}...")
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    start_time = datetime(2026, 1, 1, 0, 0, 0)
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "sensor_location", "grid_voltage", "flood_index", "route_congestion", "is_anomaly"])
        
        for i in range(10000):
            current_time = start_time + timedelta(minutes=i*5)
            location = random.choice(LOCATIONS)
            
            # Base logic
            voltage_base = 220.0
            voltage = voltage_base + (math.sin(i * 0.1) * 5) + random.uniform(-2.0, 2.0)
            
            flood_index = max(0.0, math.sin(i * 0.05) * 0.2 + random.uniform(0.0, 0.1))
            congestion = int(max(10, min(95, 40 + (math.cos(i * 0.05) * 30) + random.uniform(-10, 10))))
            
            is_anomaly = 0
            # Inject anomaly (e.g. 2% of the time)
            if random.random() > 0.98:
                flood_index += random.uniform(0.6, 0.9)
                voltage -= random.uniform(20.0, 50.0)
                is_anomaly = 1
                
            writer.writerow([
                current_time.isoformat(),
                location,
                round(voltage, 2),
                round(flood_index, 2),
                congestion,
                is_anomaly
            ])
            
    print("Dataset generation complete. Saved to artifacts folder.")

if __name__ == "__main__":
    generate_10k_dataset()
