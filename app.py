import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys from .env
REAL_ESTATE_API_KEY = os.getenv("REAL_ESTATE_API_KEY")
CRIME_API_KEY = os.getenv("CRIME_API_KEY")
SCHOOLDIGGER_APP_ID = os.getenv("SCHOOLDIGGER_APP_ID")
SCHOOLDIGGER_APP_KEY = os.getenv("SCHOOLDIGGER_APP_KEY")

# Function to get coordinates for a place using Nominatim (OpenStreetMap)
def get_coordinates(place_name):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={place_name}"
    response = requests.get(url).json()
    if response:
        return float(response[0]['lat']), float(response[0]['lon'])
    return None, None

# Function to get school ratings from SchoolDigger API
def get_school_data(lat, lon):
    url = f"https://api.schooldigger.com/v1.2/schools?lat={lat}&lon={lon}&distance=5&appID={SCHOOLDIGGER_APP_ID}&appKey={SCHOOLDIGGER_APP_KEY}"
    response = requests.get(url)
    schools = []
    if response.status_code == 200:
        data = response.json()
        for school in data.get('schoolList', []):
            rank_history = school.get('rankHistory')
            rating = "N/A"
            if rank_history and isinstance(rank_history, list) and len(rank_history) > 0:
                rating = rank_history[0].get('rank', "N/A")
            schools.append({
                'name': school.get('schoolName', 'Unknown'),
                'rating': rating,
                'gradeRange': f"{school.get('lowGrade', '')}–{school.get('highGrade', '')}",
                'type': school.get('schoolType', 'N/A'),
                'address': school.get('address', {}).get('street', 'N/A')
            })
    return schools

# Function to get real estate summary data (stubbed with example)
def get_real_estate_data(place):
    # Replace with your actual API integration here
    return {
        'median_price': "$675,000",
        'average_price_per_sqft': "$325",
        'trending': "Upward trend in last 6 months"
    }

# Function to get crime data from Crimeometer API
def get_crime_data(lat, lon):
    url = "https://api.crimeometer.com/v1/incidents/raw"
    headers = {"Content-Type": "application/json", "x-api-key": CRIME_API_KEY}
    body = {
        "lat": lat,
        "lon": lon,
        "distance": "5mi",
        "datetime_ini": "2023-06-01T00:00:00.000Z",
        "datetime_end": "2024-06-01T23:59:59.999Z"
    }
    response = requests.post(url, json=body, headers=headers)
    crime_count = 0
    if response.status_code == 200:
        data = response.json()
        crime_count = len(data.get("incidents", []))
    return crime_count

# Function to format and display neighborhood summary
def display_neighborhood_summary(place):
    st.subheader(place)
    lat, lon = get_coordinates(place)

    if not lat or not lon:
        st.error("Could not fetch location coordinates.")
        return

    # School Ratings
    st.markdown("**Schools:**")
    schools = get_school_data(lat, lon)
    if schools:
        for school in schools[:3]:
            st.markdown(f"- **{school['name']}** (Rating: {school['rating']}) - {school['gradeRange']} - {school['type']}")
    else:
        st.write("No schools data available.")

    # Real Estate Data
    st.markdown("**Real Estate:**")
    real_estate = get_real_estate_data(place)
    st.markdown(f"- Median Price: {real_estate['median_price']}")
    st.markdown(f"- Avg Price/Sqft: {real_estate['average_price_per_sqft']}")
    st.markdown(f"- Trend: {real_estate['trending']}")

    # Crime Data
    st.markdown("**Crime Statistics:**")
    crimes = get_crime_data(lat, lon)
    st.markdown(f"- Reported Incidents in Last Year: {crimes}")

# Streamlit UI
st.title("Neighborhood Insights Bot")
st.markdown("Compare two neighborhoods in terms of schools, real estate, and crime.")

place_input = st.text_input("Enter comparison (e.g., 'Hopkinton, MA vs Framingham, MA'):")

if place_input and "vs" in place_input:
    place1, place2 = [p.strip() for p in place_input.split("vs")]
    col1, col2 = st.columns(2)

    with col1:
        display_neighborhood_summary(place1)

    with col2:
        display_neighborhood_summary(place2)

    # Optional: follow-up prompt
    st.markdown("\n---")
    followup = st.text_input("Ask a follow-up question about either neighborhood:")
    if followup:
        st.write("🔍 This feature is coming soon!")
else:
    st.info("Please enter two neighborhoods to compare in the correct format.")
