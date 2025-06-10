import pandas as pd
import streamlit as st
import requests

# Geocoding Function using OpenCage
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
    (
      node[{key}="{value}"](around:{radius},{lat},{lon});
      way[{key}="{value}"](around:{radius},{lat},{lon});
      relation[{key}="{value}"](around:{radius},{lat},{lon});
    );
    out center;
    """
    url = "http://overpass-api.de/api/interpreter"
    try:
        response = requests.get(url, params={'data': query}, timeout=15)
        response.raise_for_status()
        data = response.json()
        places = []
        for element in data.get('elements', []):
            tags = element.get('tags', {})
            name = tags.get('name', 'Unnamed')
            places.append(name)
        return places[:5] if places else ["No results found"]
    except:
        return ["Error retrieving data"]

# Streamlit UI
st.set_page_config(page_title="Compare Places", layout="centered")
st.title("Compare Two Places")
st.markdown("Enter two locations to compare nearby parks, gyms, schools, and shops (free API version).")

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
        # Show map
        locations = [
            {'lat': lat1, 'lon': lon1, 'place': place1},
            {'lat': lat2, 'lon': lon2, 'place': place2}
        ]
        df_map = pd.DataFrame(locations)
        st.subheader("📍 Location Map")
        st.map(df_map)

        # Side-by-side comparison
        col1, col2 = st.columns(2)

        with col1:
            st.subheader(f"📌 {place1}")
            st.write(f"Latitude: {lat1:.4f}, Longitude: {lon1:.4f}")
            st.write("🏞️ Nearby Parks:")
            st.write(get_nearby_places(lat1, lon1, 'leisure=park', 'parks'))
            st.write("🏋️ Nearby Gyms:")
            st.write(get_nearby_places(lat1, lon1, 'leisure=fitness_centre', 'gyms'))
            st.write("🏫 Nearby Schools:")
            st.write(get_nearby_places(lat1, lon1, 'amenity=school', 'schools'))
            st.write("🛍️ Nearby Shops:")
            st.write(get_nearby_places(lat1, lon1, 'shop', 'shops'))

        with col2:
            st.subheader(f"📌 {place2}")
            st.write(f"Latitude: {lat2:.4f}, Longitude: {lon2:.4f}")
            st.write("🏞️ Nearby Parks:")
            st.write(get_nearby_places(lat2, lon2, 'leisure=park', 'parks'))
            st.write("🏋️ Nearby Gyms:")
            st.write(get_nearby_places(lat2, lon2, 'leisure=fitness_centre', 'gyms'))
            st.write("🏫 Nearby Schools:")
            st.write(get_nearby_places(lat2, lon2, 'amenity=school', 'schools'))
            st.write("🛍️ Nearby Shops:")
            st.write(get_nearby_places(lat2, lon2, 'shop', 'shops'))
