import pandas as pd
import streamlit as st
import requests
import random

# Geocoding Function using OpenCageData API
def geocode_location(place_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': place_name,
        'key': '8e8875148f2f42e791dd420015550342',
        'limit': 1,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data['results']:
            return data['results'][0]['geometry']['lat'], data['results'][0]['geometry']['lng']
    except Exception as e:
        print(f"Error: {e}")
    return None, None

# Function to Get Nearby Places using Overpass API 
def get_nearby_places(lat, lon, key, value, radius=1500):
    query = f"""
    [out:json];
    node[{key}={value}](around:{radius},{lat},{lon});
    out;
    """
    url = "http://overpass-api.de/api/interpreter"
    try:
        response = requests.get(url, params={'data': query}, timeout=15)
        response.raise_for_status()
        data = response.json()
        places = []
        for element in data.get('elements', []):
            name = element.get('tags', {}).get('name', 'Unnamed')
            places.append(name)
        return places[:5]  # Limit to 5 results
    except:
        return ["Error retrieving data"]

# Dummy metric functions (replace with real data if possible)
def get_crime_rate(place):
    return random.choice(["Low", "Medium", "High"])

def get_commute_score_and_type(place):
    return random.randint(50, 90), random.choice(["Bus & Train", "Subway", "Car"])

def get_walkability_score(place):
    return random.randint(40, 90)

def get_diversity_index(place):
    return round(random.uniform(0.3, 0.9), 2)

def get_avg_housing_cost(place):
    costs = {
        "Back Bay, Boston, MA": "$850,000",
        "South Boston, MA": "$700,000",
        "default": "$450,000"
    }
    return costs.get(place, costs["default"])

def calculate_pet_score(green_space_count, walkability_score):
    return round((green_space_count * 20 + walkability_score) / 2)

# Streamlit UI
st.set_page_config(page_title="Compare Two Places", layout="centered")
st.title("Compare Two Places")
st.markdown("Enter two locations to compare housing, crime, schools, commute, green space, gyms, shopping, and more.")

place1 = st.text_input("Enter First Location", "Back Bay, Boston, MA")
place2 = st.text_input("Enter Second Location", "South Boston, MA")

if st.button("Compare"):
    lat1, lon1 = geocode_location(place1)
    lat2, lon2 = geocode_location(place2)

    if lat1 is None or lon1 is None:
        st.error(f"Couldn't locate **{place1}**. Try a more specific name.")
    elif lat2 is None or lon2 is None:
        st.error(f"Couldn't locate **{place2}**. Try a more specific name.")
    else:
        # Show location map
        locations = [
            {'lat': lat1, 'lon': lon1, 'place': place1},
            {'lat': lat2, 'lon': lon2, 'place': place2}
        ]
        df_map = pd.DataFrame(locations)
        st.subheader("📍 Location Map")
        st.map(df_map)

        # Helper to fetch all metrics for a place
        def get_place_data(place, lat, lon):
            parks = get_nearby_places(lat, lon, 'leisure', 'park')
            gyms = get_nearby_places(lat, lon, 'amenity', 'gym')
            schools = get_nearby_places(lat, lon, 'amenity', 'school')
            shopping = get_nearby_places(lat, lon, 'shop', 'yes')
            crime = get_crime_rate(place)
            commute_score, commute_type = get_commute_score_and_type(place)
            walk_score = get_walkability_score(place)
            diversity = get_diversity_index(place)
            housing_cost = get_avg_housing_cost(place)
            pet_score = calculate_pet_score(len(parks), walk_score)

            return {
                "Avg Housing Cost": housing_cost,
                "Crime Rate": crime,
                "Nearby Schools": schools,
                "Commute Score": commute_score,
                "Commute Type": commute_type,
                "Green Space (Parks Count)": len(parks),
                "Walkability Score": walk_score,
                "Diversity Index": diversity,
                "Nearby Gyms": gyms,
                "PET Score": pet_score,
                "Nearby Shopping": shopping
            }

        data1 = get_place_data(place1, lat1, lon1)
        data2 = get_place_data(place2, lat2, lon2)

        # Display side-by-side tables
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📌 {place1}")
            for key, val in data1.items():
                if isinstance(val, list):
                    st.write(f"**{key}:**")
                    for item in val:
                        st.write(f"- {item}")
                else:
                    st.write(f"**{key}:** {val}")

        with col2:
            st.subheader(f"📌 {place2}")
            for key, val in data2.items():
                if isinstance(val, list):
                    st.write(f"**{key}:**")
                    for item in val:
                        st.write(f"- {item}")
                else:
                    st.write(f"**{key}:** {val}")
