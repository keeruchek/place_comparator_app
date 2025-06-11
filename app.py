import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys and base URLs
CRIME_DATA_API = os.getenv("CRIME_DATA_API")
REAL_ESTATE_API = os.getenv("REAL_ESTATE_API")
HOSPITAL_API = os.getenv("HOSPITAL_API")
GYM_API = os.getenv("GYM_API")
GROCERY_API = os.getenv("GROCERY_API")
COMMUTE_API = os.getenv("COMMUTE_API")
SCHOOL_DATA_API_KEY = os.getenv("SCHOOL_DATA_API_KEY")
SCHOOL_DATA_BASE_URL = os.getenv("SCHOOL_DATA_BASE_URL")

# Functions for each API
def get_crime_data(city):
    try:
        response = requests.get(f"{CRIME_DATA_API}?city={city}")
        return response.json()
    except:
        return {}

def get_real_estate_data(city):
    try:
        response = requests.get(f"{REAL_ESTATE_API}?city={city}")
        return response.json()
    except:
        return {}

def get_hospitals(city):
    try:
        response = requests.get(f"{HOSPITAL_API}?city={city}")
        return response.json()
    except:
        return {}

def get_gyms(city):
    try:
        response = requests.get(f"{GYM_API}?city={city}")
        return response.json()
    except:
        return {}

def get_grocery_stores(city):
    try:
        response = requests.get(f"{GROCERY_API}?city={city}")
        return response.json()
    except:
        return {}

def get_commute_score(city):
    try:
        response = requests.get(f"{COMMUTE_API}?city={city}")
        return response.json()
    except:
        return {}

def get_school_data(zip_code):
    try:
        response = requests.get(
            f"{SCHOOL_DATA_BASE_URL}?zip={zip_code}&key={SCHOOL_DATA_API_KEY}"
        )
        return response.json()
    except:
        return []

def get_all_metrics(city, zip_code):
    return {
        "crime": get_crime_data(city),
        "real_estate": get_real_estate_data(city),
        "hospitals": get_hospitals(city),
        "gyms": get_gyms(city),
        "groceries": get_grocery_stores(city),
        "commute": get_commute_score(city),
        "schools": get_school_data(zip_code),
    }

# Streamlit UI
st.title("City Metrics Dashboard")
city = st.text_input("Enter a city")
zip_code = st.text_input("Enter ZIP code")

if st.button("Get Metrics"):
    if city and zip_code:
        metrics = get_all_metrics(city, zip_code)

        st.header("Crime Data")
        st.json(metrics["crime"])

        st.header("Real Estate Data")
        st.json(metrics["real_estate"])

        st.header("Hospitals")
        st.json(metrics["hospitals"])

        st.header("Gyms")
        st.json(metrics["gyms"])

        st.header("Grocery Stores")
        st.json(metrics["groceries"])

        st.header("Commute Score")
        st.json(metrics["commute"])

        st.header("Schools")
        if metrics["schools"]:
            for school in metrics["schools"]:
                st.markdown(
                    f"**{school.get('name', 'N/A')}** - {school.get('level', 'N/A')}, Rating: {school.get('rating', 'N/A')}/10"
                )
        else:
            st.write("No school data found.")
    else:
        st.warning("Please enter both city and ZIP code.")
