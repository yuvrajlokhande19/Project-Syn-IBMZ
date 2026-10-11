import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# OpenRouteService API Token
DEFAULT_ORS_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImMzYzc5ZGUzNjEyNjRiMzA5ODM3NjQ5NzVlYjQzZTY1IiwiaCI6Im11cm11cjY0In0="
API_KEY = os.getenv("OPENROUTESERVICE_KEY", DEFAULT_ORS_KEY).strip()

HOSPITALS = {
    "GMC_Nagpur": [79.0991, 21.1284],  # [lon, lat]
    "Mayo_Hospital": [79.1001, 21.1528],
    "AIIMS_Nagpur": [79.0435, 21.0560],
    "Lata_Mangeshkar_Hospital": [79.0550, 21.1250],
    "Wockhardt_Hospital": [79.0800, 21.1400]
}

INCIDENTS = {
    "Wardha_Road_Crash": [79.0664, 21.1000],
    "Sadar_Traffic": [79.0835, 21.1580],
    "Sitabuldi_Flood": [79.0830, 21.1450]
}

def fetch_route(start, end):
    """
    Fetches real-world road geometry from OpenRouteService.
    Falls back gracefully to Open Source Routing Machine (OSRM) if ORS is rate-limited.
    """
    # 1. Primary: OpenRouteService
    if API_KEY:
        headers = {
            'Accept': 'application/json, application/geo+json',
            'Authorization': API_KEY,
            'Content-Type': 'application/json; charset=utf-8'
        }
        body = {"coordinates": [start, end]}
        url = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                if "features" in data and len(data["features"]) > 0:
                    return data["features"][0]
            else:
                print(f"[ORS NOTICE] Status {response.status_code}: {response.text[:100]}. Falling back to OSRM...")
        except Exception as e:
            print(f"[ORS EXCEPTION] {e}. Cascading to OSRM...")

    # 2. Resilient Fallback: OSRM
    try:
        osrm_url = f"https://router.project-osrm.org/route/v1/driving/{start[0]},{start[1]};{end[0]},{end[1]}?overview=full&geometries=geojson"
        res = requests.get(osrm_url, timeout=5.0)
        if res.status_code == 200:
            routes = res.json().get("routes", [])
            if routes:
                geom = routes[0].get("geometry", {})
                return {
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {
                        "summary": {
                            "distance": routes[0].get("distance", 15000),
                            "duration": routes[0].get("duration", 900)
                        },
                        "source": "OSRM_FALLBACK"
                    }
                }
    except Exception as osrm_err:
        print(f"[OSRM EXCEPTION] {osrm_err}")

    return None

def build_cache():
    cache = {}
    print(f"[ORS ROUTING ENGINE] Initializing road corridor calculation across {len(HOSPITALS)} hospitals...")
    
    # Pre-calculate corridors between hospitals and incident nodes
    for h_name, h_coords in HOSPITALS.items():
        for i_name, i_coords in INCIDENTS.items():
            route_key = f"{i_name}_to_{h_name}"
            print(f"Fetching corridor: {route_key}...")
            feature = fetch_route(i_coords, h_coords)
            if feature:
                cache[route_key] = feature
            time.sleep(0.5)

    # Pre-calculate inter-hospital green corridors (for organ transfer / emergency diversion)
    hospital_names = list(HOSPITALS.keys())
    for i in range(len(hospital_names)):
        for j in range(i + 1, len(hospital_names)):
            h1 = hospital_names[i]
            h2 = hospital_names[j]
            route_key = f"{h1}_to_{h2}"
            print(f"Fetching inter-hospital green corridor: {route_key}...")
            feature = fetch_route(HOSPITALS[h1], HOSPITALS[h2])
            if feature:
                cache[route_key] = feature
            time.sleep(0.5)

    # Save to artifacts directory (Pair 2 domain)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(base_dir, '..', 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    artifacts_cache = os.path.join(artifacts_dir, 'road_corridors_cache.json')
    with open(artifacts_cache, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)
    print(f"Offline road corridors successfully cached -> {artifacts_cache} ({len(cache)} corridors)")

    # Also mirror to command center data directory if available
    cmd_dir = os.path.join(base_dir, '..', '..', '01-command-center', 'data')
    if os.path.exists(os.path.dirname(cmd_dir)):
        os.makedirs(cmd_dir, exist_ok=True)
        frontend_cache = os.path.join(cmd_dir, 'routes_cache.json')
        with open(frontend_cache, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        print(f"Mirrored route cache to frontend directory -> {frontend_cache}")

if __name__ == "__main__":
    build_cache()

