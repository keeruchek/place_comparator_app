import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys from .env
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
SCHOOLDIGGER_API_KEY = os.getenv("SCHOOLDIGGER_API_KEY")
ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY")

st.set_page_config(page_title="Real Estate Helper", layout="centered")

st.title("🏠 Real Estate Search Helper")

# Address input
address = st.text_input("Enter an address:")

if address:
    st.subheader("📍 Location Details")

    # Geocoding with OpenCage
    geocode_url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={OPENCAGE_API_KEY}"
    geocode_response = requests.get(geocode_url)
    geo_data = geocode_response.json()

    try:
        lat = geo_data['results'][0]['geometry']['lat']
        lng = geo_data['results'][0]['geometry']['lng']
        st.write(f"**Latitude:** {lat}")
        st.write(f"**Longitude:** {lng}")
    except (IndexError, KeyError):
        st.error("Could not get location data. Please check the address.")

    # School info from SchoolDigger
    st.subheader("🎓 Nearby Schools")
    school_url = (
        f"https://api.schooldigger.com/v1.2/schools?st=CA&lat={lat}&lon={lng}&distance=5"
        f"&appID=DUMMY_ID&appKey={SCHOOLDIGGER_API_KEY}"
    )
    school_response = requests.get(school_url)
    school_data = school_response.json()

    if school_data.get("schoolList"):
        for school in school_data["schoolList"][:3]:  # Show top 3
            st.markdown(f"**{school['schoolName']}**")
            st.write(f"Rating: {school.get('rankStars', 'N/A')}")
            st.write(f"Address: {school['address']}")
            st.markdown("---")
    else:
        st.write("No nearby schools found.")

    # Placeholder Zillow integration
    st.subheader("💰 Estimated Property Value")
    st.write("Zillow API requires partnership access. Placeholder for property value.")
