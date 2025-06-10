import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# Function to get lat/lon using Nominatim
def geocode_location(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json"}
    response = requests.get(url, params=params).json()
    if response:
        return float(response[0]['lat']), float(response[0]['lon'])
    else:
        return None, None

# Function to fetch Overpass data
def get_nearby_places(lat, lon, key, value=None, radius=1000):
    value_filter = f'["{key}"="{value}"]' if value else f'["{key}"]'
    query = f"""
    [out:json];
    (
      node{value_filter}(around:{radius},{lat},{lon});
      way{value_filter}(around:{radius},{lat},{lon});
      relation{value_filter}(around:{radius},{lat},{lon});
    );
    out center;
    """
    url = "http://overpass-api.de/api/interpreter"
    response = requests.post(url, data=query)
    data = response.json()
    return len(data.get("elements", []))

# Simulated data functions
def get_avg_rent():
    return {
        "Studio": "$1200",
        "1 Bed": "$1500",
        "2 Bed": "$1800"
    }

def get_crime_rate():
    return "Medium"

def get_commute_score():
    return {
        "Score": 70,
        "Transit Options": ["Bus", "Subway"]
    }

def get_diversity_index():
    return 78

def get_parking_score():
    return "High"

# Combined metric function
def get_all_metrics(place_name, lat, lon):
    rent = get_avg_rent()
    crime = get_crime_rate()
    commute = get_commute_score()
    diversity = get_diversity_index()
    parking = get_parking_score()

    parks = get_nearby_places(lat, lon, 'leisure', 'park')
    gyms = get_nearby_places(lat, lon, 'leisure', 'fitness_centre')
    shopping = get_nearby_places(lat, lon, 'shop')  # any type of shop
    hospitals = get_nearby_places(lat, lon, 'amenity', 'hospital')
    schools = get_nearby_places(lat, lon, 'amenity', 'school')
    colleges = get_nearby_places(lat, lon, 'amenity', 'college')

    walkability = "High" if parks > 3 and gyms > 2 else "Medium"
    green_score = "High" if parks > 5 else "Medium"
    pet_score = "High" if green_score == "High" and walkability == "High" else "Medium"

    return {
        "Average Rent": rent,
        "Crime Rate": crime,
        "Commute Score": commute,
        "Green Space Score": green_score,
        "Walkability Score": walkability,
        "Pet Score": pet_score,
        "Gyms Nearby": gyms,
        "Shopping Centres/Grocery Stores Nearby": shopping,
        "Hospitals Nearby": hospitals,
        "Schools/Colleges Nearby": schools + colleges,
        "Diversity Index": diversity,
        "Parking Score": parking
    }

# Streamlit UI
st.set_page_config(page_title="Place Comparator", layout="wide")
st.title("🏡 Place Comparator App")

place1 = st.text_input("Enter location name:")

if place1:
    lat1, lon1 = geocode_location(place1)
    if lat1 and lon1:
        data1 = get_all_metrics(place1, lat1, lon1)

        st.subheader(f"📍 {place1} Overview")
        st.json(data1)

        st.subheader("📌 Map")
        m = folium.Map(location=[lat1, lon1], zoom_start=14)
        folium.Marker([lat1, lon1], popup=place1).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.error("Couldn't locate the place. Try a more specific name.")
