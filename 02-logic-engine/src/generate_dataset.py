import csv
import random
import math
import os
from datetime import datetime, timedelta, timezone

# Realistic Locations in Nagpur based on the hospital grid map
LOCATIONS = [
    "GMC_Nagpur",
    "Mayo_Hospital",
    "AIIMS_Nagpur",
    "Lata_Mangeshkar_Hospital",
    "Wockhardt_Hospital"
]

def generate_10k_dataset(filename=None):
    """
    Generates 10,000 synthetic hospital telemetry records with deterministic signal modeling.
    Features:
    - grid_voltage: Baseline 220V with harmonic variation and noise (~216-224V). Drops during grid collapse.
    - water_pressure: Hospital ICU water pressure in PSI (~45-60 PSI). Drops during supply rupture.
    - flood_index: Water levels normalized 0.0 to 1.0 (nominal < 0.25). Spikes > 0.8 during flash floods.
    - route_congestion: Traffic congestion percentage 10-95% (nominal ~30-55%). Spikes during road blockages.
    - is_anomaly: Binary ground-truth label (0 for nominal, 1 for critical anomaly).
    """
    if filename is None:
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'artifacts', 'synthetic_hospital_data_10k.csv')

    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    print(f"Generating 10,000 synthetic hospital records -> {filename}...")

    # Fixed seed for strict reproducibility
    random.seed(42)

    start_time = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp",
            "sensor_location",
            "grid_voltage",
            "water_pressure",
            "flood_index",
            "route_congestion",
            "is_anomaly"
        ])

        for i in range(10000):
            current_time = start_time + timedelta(minutes=i * 5)
            location = random.choice(LOCATIONS)

            # Harmonic base signal with noise
            voltage_base = 220.0
            voltage = voltage_base + (math.sin(i * 0.1) * 4.0) + random.uniform(-1.5, 1.5)

            water_base = 52.0
            water_pressure = water_base + (math.cos(i * 0.08) * 3.0) + random.uniform(-1.0, 1.0)

            flood_index = max(0.0, math.sin(i * 0.04) * 0.15 + random.uniform(0.01, 0.08))
            congestion = int(max(10, min(95, 40 + (math.cos(i * 0.05) * 25) + random.uniform(-8, 8))))

            is_anomaly = 0
            rand_val = random.random()

            # Controlled Anomaly Injection (~4% of total dataset)
            if rand_val > 0.98:
                # Scenario A: Severe Urban Flood
                flood_index += random.uniform(0.65, 0.85)  # Crosses critical threshold > 0.8
                congestion = min(98, congestion + random.randint(35, 45))
                voltage -= random.uniform(10.0, 25.0)
                water_pressure += random.uniform(15.0, 30.0)  # Storm surge pressure
                is_anomaly = 1
            elif rand_val < 0.02:
                # Scenario B: Power Grid Collapse & Auxiliary Failure
                voltage = random.uniform(20.0, 85.0)  # Severe blackout
                congestion = min(95, congestion + random.randint(30, 40))
                water_pressure = random.uniform(5.0, 15.0)  # Auxiliary pump failure
                is_anomaly = 1

            writer.writerow([
                current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                location,
                round(voltage, 2),
                round(water_pressure, 2),
                round(flood_index, 2),
                congestion,
                is_anomaly
            ])

    print("Dataset generation complete. Saved to artifacts folder.")

if __name__ == "__main__":
    generate_10k_dataset()
