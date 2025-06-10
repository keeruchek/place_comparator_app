 import pandas as pd
import streamlit as st
import requests
import random

# 🗺️ Geocoding using OpenCage Geocoder
def geocode_location(place_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {'q': place_name, 'key': '8e8875148f2f42e791dd420015550342', 'limit': 1}
    try:
        resp = requests.get(url, params=params, timeout=10).json()
        if resp.get('results'):
            geo = resp['results'][0]['geometry']
            return geo['lat'], geo['lng']
    except:
        pass
    return None, None

# 🔍 Nearby places via Overpass API
def get_nearby_places(lat, lon, filter_query, label, radius=1500):
    query = f"""
      [out:json];
      node[{filter_query}](around:{radius},{lat},{lon});
      way[{filter_query}](around:{radius},{lat},{lon});
      relation[{filter_query}](around:{radius},{lat},{lon});
      out center;
    """
    try:
        data = requests.get("http://overpass-api.de/api/interpreter", params={'data': query}, timeout=15).json()
        places = []
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            name = tags.get('name', 'Unnamed')
            lat0 = el.get('lat') or el.get('center', {}).get('lat')
            lon0 = el.get('lon') or el.get('center', {}).get('lon')
            places.append(f"{name} ({lat0:.4f}, {lon0:.4f})")
        return places[:5] if places else [f"No {label} found"]
    except Exception as e:
        return [f"Error {label}: {e}"]

# Dummy helpers
def avg_housing_cost(place):
    # Simulated values; integrate real data source like RentCast
    return {'studio': '$1,200', '1 bed': '$1,800', '2 bed': '$2,400'}

def crime_rate(place):
    return random.choice(['Low', 'Medium', 'High'])

def commute_info(place):
    return random.randint(50, 100), random.choice(['Bus', 'Train', 'Tram', 'Bus & Train'])

def walkability(place):
    return random.randint(40, 95)

def diversity_index(place):
    return round(random.uniform(0.3, 0.9), 2)

def pet_score(green_count, walk_score):
    return round((green_count * 10 + walk_score) / 2)

def parking_score(lat, lon):
    # Count nearby parking amenities
    parks = get_nearby_places(lat, lon, 'amenity=parking', 'parking')
    return len(parks)

def get_all_metrics(place, lat, lon):
    parks = get_nearby_places(lat, lon, 'leisure=park', 'parks')
    gyms = get_nearby_places(lat, lon, 'leisure=fitness_centre', 'gyms')
    schools = get_nearby_places(lat, lon, 'amenity=school', 'schools')
    shopping = get_nearby_places(lat, lon, 'shop', 'shops')
    hospitals = get_nearby_places(lat, lon, 'amenity=hospital', 'hospitals')
    parking_ct = parking_score(lat, lon)
    
    housing = avg_housing_cost(place)
    crime = crime_rate(place)
    commute_sc, commute_type = commute_info(place)
    walk_sc = walkability(place)
    div_ix = diversity_index(place)
    pet_sc = pet_score(len(parks), walk_sc)
    
    return {
        "Housing (Studio)": housing['studio'],
        "Housing (1 bed)": housing['1 bed'],
        "Housing (2 bed)": housing['2 bed'],
        "Crime Rate": crime,
        "Schools Nearby": schools,
        "Commute Score": commute_sc,
        "Transit Type": commute_type,
        "Green Space (parks count)": len(parks),
        "Walkability Score": walk_sc,
        "Gyms Nearby": gyms,
        "Shopping Nearby": shopping,
        "Hospitals Nearby": hospitals,
        "Parking Score (count)": parking_ct,
        "Diversity Index": div_ix,
        "PET Score": pet_sc
    }

# 🧭 Streamlit UI Setup
st.set_page_config(page_title="Neighborhood Insights", layout="centered")
st.title("🏡 Neighborhood Insights & Comparison Tool")

mode = st.radio("Mode:", ("Compare Two Places", "Single Place"))
place1 = st.text_input("Place 1 (City, State)", "Cambridge, MA")
place2 = st.text_input("Place 2 (City, State)", "Somerville, MA") if mode == "Compare Two Places" else None

if st.button("Show Insights"):
    lat1, lon1 = geocode_location(place1)
    lat2, lon2 = (None, None)
    if mode == "Compare Two Places":
        lat2, lon2 = geocode_location(place2)

    if lat1 is None:
        st.error(f"Couldn't locate {place1}")
        st.stop()
    if mode == "Compare Two Places" and lat2 is None:
        st.error(f"Couldn't locate {place2}")
        st.stop()

    # Show map
    locs = [{'lat': lat1,'lon':lon1,'place':place1}]
    if mode == "Compare Two Places":
        locs.append({'lat':lat2,'lon':lon2,'place':place2})
    st.map(pd.DataFrame(locs))

    data1 = get_all_metrics(place1, lat1, lon1)
    data2 = get_all_metrics(place2, lat2, lon2) if mode=="Compare Two Places" else None

    if mode=="Compare Two Places":
        col1, col2 = st.columns(2)
        for col, place, data in [(col1, place1, data1), (col2, place2, data2)]:
            with col:
                st.subheader(place)
                for k,v in data.items():
                    if isinstance(v, list):
                        st.markdown(f"**{k}:**")
                        for item in v:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{k}:** {v}")
    else:
        st.subheader(place1)
        for k,v in data1.items():
            if isinstance(v, list):
                st.markdown(f"**{k}:**")
                for item in v:
                    st.markdown(f"- {item}")
            else:
                st.markdown(f"**{k}:** {v}")
