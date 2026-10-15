import csv
import random
import math
import os
from datetime import datetime, timedelta, timezone

MUMBAI_LOCATIONS = [
    "KEM_Hospital_Parel",
    "Sion_Hospital_LTMMC",
    "Sir_JJ_Hospital_Byculla",
    "BYL_Nair_Hospital",
    "Tata_Memorial_Hospital",
    "Lilavati_Hospital_Bandra",
    "Hinduja_Hospital_Mahim",
    "Cooper_Hospital_Juhu",
    "Nanavati_Max_VileParle",
    "Kokilaben_Hospital_Andheri",
    "Bombay_Hospital_MarineLines",
    "Saifee_Hospital_CharniRoad",
    "St_George_Hospital_CSMT",
    "GT_Hospital_DhobiTalao",
    "HBT_Trauma_Care_Jogeshwari",
    "Hindmata_Lowland_Basin",
    "Gandhi_Market_KingCircle",
    "Milan_Subway_Santacruz",
    "Andheri_Subway_West",
    "Kurla_LBS_Marg_Bottleneck"
]

def generate_mumbai_50k_telemetry():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(base_dir, '..', 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    telemetry_file = os.path.join(artifacts_dir, 'mumbai_historical_disaster_dataset.csv')
    synthetic_10k_file = os.path.join(artifacts_dir, 'synthetic_hospital_data_10k.csv')

    print(f"[DATASET] Generating 50,000 Mumbai Historical Telemetry Records -> {telemetry_file}...")
    random.seed(1926)  # 1926: KEM Hospital foundation year

    start_time = datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc)

    records = []
    with open(telemetry_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "sensor_location",
            "grid_voltage",
            "water_pressure",
            "flood_index",
            "route_congestion",
            "ward_oxygen_kpa",
            "icu_occupancy_pct",
            "incident_type",
            "is_anomaly"
        ])

        for i in range(50000):
            # 5-minute sampling interval spanning monsoon season & operations
            curr_time = start_time + timedelta(minutes=i * 5)
            loc = random.choice(MUMBAI_LOCATIONS)

            # Diurnal baseline cycles
            hour = curr_time.hour
            month = curr_time.month

            # Monsoon factor (June - September)
            is_monsoon = 6 <= month <= 9
            rain_bias = 0.15 if is_monsoon else 0.02

            # Baseline signals
            grid_v = 220.0 + math.sin(i * 0.05) * 3.5 + random.uniform(-1.2, 1.2)
            water_p = 50.0 + math.cos(i * 0.04) * 4.0 + random.uniform(-1.0, 1.0)
            base_flood = max(0.0, (math.sin(i * 0.02) * 0.1) + rain_bias + random.uniform(0.01, 0.06))
            
            # Traffic congestion: peak at 9am-12pm and 5pm-9pm
            is_peak = (9 <= hour <= 12) or (17 <= hour <= 21)
            traffic_base = 65 if is_peak else 35
            congestion = int(max(10, min(98, traffic_base + (math.sin(i * 0.03) * 18) + random.uniform(-6, 6))))

            ward_o2 = 420.0 + random.uniform(-15.0, 15.0) # nominal 400-440 kPa
            icu_occ = int(max(60, min(99, 82 + math.sin(i * 0.01) * 10 + random.uniform(-4, 4))))
            incident_type = "Nominal"
            is_anomaly = 0

            # Injected historical disaster scenarios (~5.5% probability)
            rand_val = random.random()
            if rand_val < 0.025:
                # Severe Flash Flood / Inundation (Hindmata, Milan Subway, Sion)
                base_flood = round(random.uniform(0.78, 0.98), 2)
                congestion = min(99, congestion + random.randint(30, 45))
                grid_v -= random.uniform(15.0, 35.0)
                water_p += random.uniform(18.0, 32.0)
                incident_type = "Lowland_Inundation_FlashFlood"
                is_anomaly = 1
            elif rand_val < 0.040:
                # Substation Power Outage / Grid Sag
                grid_v = round(random.uniform(25.0, 95.0), 1)
                ward_o2 -= random.uniform(40.0, 120.0)
                incident_type = "BEST_Substation_Grid_Collapse"
                is_anomaly = 1
            elif rand_val < 0.050:
                # Liquid Medical Oxygen Depletion / Valve Rupture
                ward_o2 = round(random.uniform(180.0, 260.0), 1)
                icu_occ = min(100, icu_occ + random.randint(8, 15))
                incident_type = "Cryogenic_O2_Depletion_Alert"
                is_anomaly = 1
            elif rand_val < 0.055:
                # Severe Corridor Choke / Cyber Spoofing Traffic Stoppage
                congestion = random.randint(95, 100)
                base_flood = round(random.uniform(0.65, 0.85), 2)
                incident_type = "Ambulance_Corridor_Total_Choke"
                is_anomaly = 1

            row = [
                curr_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                loc,
                round(grid_v, 2),
                round(water_p, 2),
                round(base_flood, 2),
                congestion,
                round(ward_o2, 1),
                icu_occ,
                incident_type,
                is_anomaly
            ]
            writer.writerow(row)
            records.append(row)

    print(f"[DATASET] 50,000 records successfully generated at {telemetry_file}.")

    # Also update synthetic_hospital_data_10k.csv for backwards compatibility
    with open(synthetic_10k_file, mode='w', newline='', encoding='utf-8') as f10:
        writer10 = csv.writer(f10)
        writer10.writerow([
            "timestamp", "sensor_location", "grid_voltage", "water_pressure",
            "flood_index", "route_congestion", "is_anomaly"
        ])
        for r in records[:10000]:
            # r: timestamp, sensor_location, grid_voltage, water_pressure, flood_index, route_congestion, ward_oxygen_kpa, icu_occupancy_pct, incident_type, is_anomaly
            writer10.writerow([r[0], r[1], r[2], r[3], r[4], r[5], r[9]])

    print(f"[DATASET] Updated {synthetic_10k_file} with Mumbai telemetry baseline.")

def generate_kem_admissions_dataset():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(base_dir, '..', 'artifacts')
    admissions_file = os.path.join(artifacts_dir, 'kem_hospital_historical_admissions.csv')

    print(f"[DATASET] Generating 15,000 KEM Hospital Triage & Admission Records -> {admissions_file}...")
    random.seed(2026)

    start_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    wards = ["Apex_Trauma_ICU_4B", "Neuro_Surgical_ICU_2A", "Pediatric_Emergency_1C", "Cardiac_CCU_3A", "General_Emergency_Ward"]
    corridors = [
        "Lalbaug_Flyover_Ambulance_Corridor",
        "Dr_Ambedkar_Road_Corridor",
        "Eastern_Express_Highway",
        "Western_Express_Highway",
        "Bandra_Worli_Sea_Link_Express"
    ]

    with open(admissions_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "admission_id",
            "timestamp",
            "triage_level",
            "systolic_bp",
            "heart_rate",
            "sp_o2",
            "respiratory_rate",
            "gcs_score",
            "assigned_icu_ward",
            "transit_corridor_used",
            "transit_time_minutes"
        ])

        for i in range(15000):
            admit_time = start_date + timedelta(minutes=random.randint(10, 45) * i)
            # Triage Level: Red (Immediate/Resuscitation), Amber (Emergency), Yellow (Urgent), Green (Non-urgent)
            triage_roll = random.random()
            if triage_roll < 0.15:
                triage = "RED_PRIORITY_1"
                sbp = random.randint(60, 88)
                hr = random.randint(125, 165)
                spo2 = random.randint(75, 88)
                rr = random.randint(30, 42)
                gcs = random.randint(3, 8)
                ward = "Apex_Trauma_ICU_4B"
            elif triage_roll < 0.45:
                triage = "AMBER_PRIORITY_2"
                sbp = random.randint(90, 105)
                hr = random.randint(105, 128)
                spo2 = random.randint(89, 93)
                rr = random.randint(22, 29)
                gcs = random.randint(9, 12)
                ward = random.choice(["Neuro_Surgical_ICU_2A", "Cardiac_CCU_3A"])
            elif triage_roll < 0.80:
                triage = "YELLOW_PRIORITY_3"
                sbp = random.randint(110, 135)
                hr = random.randint(75, 100)
                spo2 = random.randint(94, 98)
                rr = random.randint(16, 21)
                gcs = random.randint(13, 14)
                ward = "Pediatric_Emergency_1C"
            else:
                triage = "GREEN_PRIORITY_4"
                sbp = random.randint(115, 125)
                hr = random.randint(68, 85)
                spo2 = random.randint(98, 100)
                rr = random.randint(12, 18)
                gcs = 15
                ward = "General_Emergency_Ward"

            transit_corr = random.choice(corridors)
            transit_mins = random.randint(8, 26)

            writer.writerow([
                f"KEM-ADM-{100000 + i}",
                admit_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                triage,
                sbp,
                hr,
                spo2,
                rr,
                gcs,
                ward,
                transit_corr,
                transit_mins
            ])

    print(f"[DATASET] 15,000 KEM triage records successfully generated at {admissions_file}.")

if __name__ == "__main__":
    generate_mumbai_50k_telemetry()
    generate_kem_admissions_dataset()
