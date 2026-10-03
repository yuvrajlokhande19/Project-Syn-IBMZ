import csv
import random
import os

hospitals = [
    {"name": "AIIMS_Nagpur", "lat": 21.0664, "lng": 79.0526},
    {"name": "GMC_Nagpur", "lat": 21.1274, "lng": 79.0835},
    {"name": "Mayo_Hospital", "lat": 21.1442, "lng": 79.0968}
]

fleet = []
for i in range(1, 21):
    base = random.choice(hospitals)
    lat = base["lat"] + random.uniform(-0.02, 0.02)
    lng = base["lng"] + random.uniform(-0.02, 0.02)
    fleet.append({
        "ambulance_id": f"AMB-{i:03d}",
        "lat": round(lat, 5),
        "lng": round(lng, 5),
        "status": random.choice(["PATROL", "DISPATCHED", "IDLE"]),
        "fuel_percent": random.randint(40, 100)
    })

os.makedirs("../artifacts", exist_ok=True)
with open("../artifacts/ambulance_fleet.csv", "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["ambulance_id", "lat", "lng", "status", "fuel_percent"])
    writer.writeheader()
    writer.writerows(fleet)

print("Ambulance fleet CSV generated.")
