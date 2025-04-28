# utils.py

import pandas as pd
import numpy as np
import requests
from math import radians, cos, sin, asin, sqrt
import openai
import zipfile

# --- Load datasets from zip ---
def load_csv_from_zip(zip_path, filename_inside_zip, **kwargs):
    with zipfile.ZipFile(zip_path) as z:
        with z.open(filename_inside_zip) as f:
            return pd.read_csv(f, **kwargs)

# Paths to community datasets
COMMUNITY_SCORE_PATH = 'community_crs_scores.csv'
COMMUNITY_AREA_PATH = 'community_areas.csv'

# Load datasets
crimes_df = load_csv_from_zip('cleaned_crimes_data.zip', 'cleaned_crimes_data.csv', parse_dates=['Date'])
community_scores_df = pd.read_csv(COMMUNITY_SCORE_PATH)
community_areas_df = pd.read_csv(COMMUNITY_AREA_PATH)

# Mapping Community Area number to Area Name
area_map = dict(zip(community_areas_df['Community Area'], community_areas_df['Area Name']))

# --- Geocoding Address ---

def get_lat_lon_from_address(address, google_api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': google_api_key
    }
    response = requests.get(base_url, params=params)
    result = response.json()

    if result['status'] == 'OK':
        location = result['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        print("Geocoding failed:", result.get('status'), result.get('error_message'))
        return None, None

# --- Distance Calculation (Haversine Formula) ---

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c * 1000  # meters

# --- Analyze Nearby Risk ---

def analyze_risk_nearby(address, lat, lon):
    crimes_df['distance'] = crimes_df.apply(lambda row: haversine_distance(lat, lon, row['Latitude'], row['Longitude']), axis=1)
    nearby = crimes_df[crimes_df['distance'] <= 500]

    if nearby.empty:
        return None

    nearest = nearby.loc[nearby['distance'].idxmin()]
    community_area = int(nearest['Community Area']) if not pd.isna(nearest['Community Area']) else None
    area_name = area_map.get(community_area, "Unknown")

    C = len(nearby)
    violent_types = ['BATTERY', 'ASSAULT', 'ROBBERY', 'HOMICIDE']
    S = len(nearby[nearby['Primary Type'].isin(violent_types)]) / C
    hours = nearby['Date'].dt.hour
    T = len(nearby[(hours >= 18) | (hours < 6)]) / C
    A = len(nearby[nearby['Arrest'] == True]) / C

    w1, w2, w3, w4 = 0.4, 0.3, 0.2, 0.1
    C_norm = np.log1p(C) / 10  # scaled
    CRS = (w1 * C_norm + w2 * S + w3 * T + w4 * (1 - A)) * 100

    community_crs = None
    if community_area is not None:
        match_row = community_scores_df[community_scores_df['Community Area'] == community_area]
        if not match_row.empty:
            community_crs = match_row.iloc[0]['CRS_Score']


    report_text = f"""
Address: {address}
Community Area: {community_area} - {area_name}
Local Risk (within 500m):
- Total Crimes: {C}
- Violent Crime Ratio: {S:.2%}
- Nighttime Crime Ratio: {T:.2%}
- Arrest Rate: {A:.2%}
- Local CRS Score: {CRS:.2f}
Community CRS Score: community_crs_display = f"{community_crs:.2f}" if community_crs is not None else "N/A"
"""

    return {
        "C": C,
        "S": S,
        "T": T,
        "A": A,
        "CRS": CRS,
        "Community_CRS": community_crs,
        "Area_Name": area_name,
        "report_text": report_text
    }

# --- Call GPT-4 for Safety Suggestion ---

def call_gpt_suggestion(prompt_text, openai_api_key):
    client = openai.OpenAI(api_key=openai_api_key)
    prompt = f"""
Below is a safety analysis report for a specific address:

{prompt_text}

Based on this report, please provide 4-5 travel safety suggestions for tourists.
Use both the area-level score and the local risk indicators within 500 meters to support your advice.
Also, determine which part of the area (East, South, West, North) the address is located in,
and compare the local crime situation with the overall community area.
"""


    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a safety advisor specializing in travel around Chicago. You provide practical travel advice for tourists."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    advice = response.choices[0].message.content
    return advice
