import streamlit as st
import requests

st.title("Test Streamlit + API Connectivity")

place = st.text_input("Enter a place name:", "Cambridge, MA")

if st.button("Test Geocode"):
    st.write("Calling geocode API...")
    try:
        url = "https://api.opencagedata.com/geocode/v1/json"
        params = {'q': place, 'key': '8e8875148f2f42e791dd420015550342', 'limit': 1}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            geo = data["results"][0]["geometry"]
            st.success(f"Lat: {geo['lat']}, Lon: {geo['lng']}")
        else:
            st.error("No results found.")
    except Exception as e:
        st.error(f"API call error: {e}")
