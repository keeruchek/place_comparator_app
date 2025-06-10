import pandas as pd
import streamlit as st
import requests

# Geocoding Function using Nominatim 
import requests

def geocode_location(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place_name,
        'format': 'json'
    }
    headers = {
        'User-Agent': 'PlaceComparatorApp/1.0 (your_email@example.com)'
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates for {place_name}: {e}")
    return None, None


# Function to Get Nearby Places using Overpass API 
def get_nearby_places(lat, lon, key, value, radius=1500):
    query = f"""
    [out:json];
    node[{key}={value}](around:{radius},{lat},{lon});
    out;
    """
    url = "http://overpass-api.de/api/interpreter"
    response = requests.get(url, params={'data': query})
    data = response.json()
    places = []
    for element in data.get('elements', []):
        name = element.get('tags', {}).get('name', 'Unnamed')
        places.append(name)
    return places[:5]  # Limit to 5 results for display

# Streamlit UI 
st.set_page_config(page_title="Compare Places", layout="centered")
st.title("Compare Two Places")
st.markdown("Enter two locations to compare nearby parks and gyms (free API version).")

place1 = st.text_input("Enter First Location", "Back Bay, Boston, MA")
place2 = st.text_input("Enter Second Location", "South Boston, MA")

if st.button("Compare"):
    lat1, lon1 = geocode_location(place1)
    lat2, lon2 = geocode_location(place2)
    #map showing locations
if lat1 and lon1:
    locations = [{'lat': lat1, 'lon': lon1, 'place': place1}]
    if lat2 and lon2:
        locations.append({'lat': lat2, 'lon': lon2, 'place': place2})

    df_map = pd.DataFrame(locations)
    st.subheader("📍 Location Map")
    st.map(df_map)


    if not lat1 or not lat2:
        st.error("Couldn't locate one or both places. Try more specific names.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📌 {place1}")
            st.write(f"Latitude: {lat1:.4f}, Longitude: {lon1:.4f}")
            st.write("🏞️ Nearby Parks:")
            st.write(get_nearby_places(lat1, lon1, 'leisure', 'park'))
            st.write("🏋️ Gyms:")
            st.write(get_nearby_places(lat1, lon1, 'amenity', 'gym'))

        with col2:
            st.subheader(f"📌 {place2}")
            st.write(f"Latitude: {lat2:.4f}, Longitude: {lon2:.4f}")
            st.write("🏞️ Nearby Parks:")
            st.write(get_nearby_places(lat2, lon2, 'leisure', 'park'))
            st.write("🏋️ Gyms:")
            st.write(get_nearby_places(lat2, lon2, 'amenity', 'gym'))
