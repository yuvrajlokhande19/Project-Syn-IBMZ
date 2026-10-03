import requests
import json
import os
import time
import base64

# Decode the ORS Key (the user provided a base64 string, but ORS keys are usually the concatenated org and id)
# The provided b64: eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImMzYzc5ZGUzNjEyNjRiMzA5ODM3NjQ5NzVlYjQzZTY1IiwiaCI6Im11cm11cjY0In0=
decoded = json.loads(base64.b64decode("eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImMzYzc5ZGUzNjEyNjRiMzA5ODM3NjQ5NzVlYjQzZTY1IiwiaCI6Im11cm11cjY0In0=").decode())
API_KEY = decoded["org"] + decoded["id"]

HOSPITALS = {
    "GMC_Nagpur": [79.0991, 21.1284],  # ORS uses [lon, lat]
    "Mayo_Hospital": [79.1001, 21.1528],
    "AIIMS_Nagpur": [79.0435, 21.0560]
}

INCIDENTS = {
    "Wardha_Road_Crash": [79.0664, 21.1000],
    "Sadar_Traffic": [79.0835, 21.1580],
    "Sitabuldi_Flood": [79.0830, 21.1450]
}

def fetch_route(start, end):
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': API_KEY,
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {"coordinates": [start, end]}
    url = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'
    
    try:
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def build_cache():
    cache = {}
    for h_name, h_coords in HOSPITALS.items():
        for i_name, i_coords in INCIDENTS.items():
            print(f"Fetching route: {i_name} -> {h_name}...")
            route_data = fetch_route(i_coords, h_coords)
            if route_data and "features" in route_data:
                cache[f"{i_name}_to_{h_name}"] = route_data["features"][0]
            time.sleep(1.5) # Avoid rate limits
            
    # Save the offline cache for the frontend to use
    os.makedirs("01-command-center/data", exist_ok=True)
    with open("01-command-center/data/routes_cache.json", "w") as f:
        json.dump(cache, f, indent=2)
    print("Offline routes cached successfully!")

if __name__ == "__main__":
    build_cache()
