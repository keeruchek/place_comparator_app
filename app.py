import pandas as pd
import streamlit as st
import requests
import random
import os
import openai

# Debug helper to show errors in UI
def show_error(message):
    st.error(message)
    print("ERROR:", message)

# 🗺️ Geocoding using OpenCage Geocoder with error handling
def geocode_location(place_name):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {'q': place_name, 'key': '8e8875148f2f42e791dd420015550342', 'limit': 1}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('results'):
            geo = data['results'][0]['geometry']
            return geo['lat'], geo['lng']
        else:
            show_error(f"No geocoding results for '{place_name}'")
            return None, None
    except Exception as e:
        show_error(f"Geocoding API error for '{place_name}': {e}")
        return None, None

# Nearby places via Overpass API with error handling
def get_nearby_places(lat, lon, query, label, radius=2000):
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node[{query}](around:{radius},{lat},{lon});
      way[{query}](around:{radius},{lat},{lon});
      relation[{query}](around:{radius},{lat},{lon});
    );
    out center;
    """
    try:
        response = requests.post(url, data={"data": query}, timeout=15)
        response.raise_for_status()
        data = response.json()
        places = []
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name")
            if name:
                places.append(name)
        if places:
            return places[:10]
        else:
            return [f"No {label} found"]
    except Exception as e:
        show_error(f"Error fetching {label}: {e}")
        return [f"Error fetching {label}: {e}"]

def avg_housing_cost(place):
    avg_rent_2bed = random.randint(1500, 3500)
    avg_price_2bed = random.randint(250000, 750000)
    return {
        'avg_rent_2bed': f"${avg_rent_2bed:,}",
        'avg_price_2bed': f"${avg_price_2bed:,}"
    }

def crime_rate(place):
    return random.choice(['Low', 'Medium', 'High'])

def commute_score(place):
    score = random.randint(1, 10)
    mode = random.choice(["car", "train", "bus", "bike", "walk"])
    return score, mode

def get_school_data(lat, lon):
    # NOTE: Replace YOUR_APP_ID and YOUR_APP_KEY with your actual SchoolDigger API keys
    url = f"https://api.schooldigger.com/v1.2/schools?st=MA&lat={lat}&lon={lon}&distance=10&appID=YOUR_APP_ID&appKey=YOUR_APP_KEY"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        schools = []
        for school in data.get('schoolList', []):
            schools.append({
                'name': school.get('schoolName'),
                'rating': school.get('rankHistory', [{}])[0].get('rank'),
                'gradeRange': school.get('lowGrade', '') + "–" + school.get('highGrade', ''),
                'type': school.get('schoolType'),
                'address': school.get('address')
            })
        if schools:
            return schools
        else:
            return [f"No schools data found"]
    except Exception as e:
        show_error(f"School data API error: {e}")
        return [f"School data API error: {e}"]

def walkability_score(lat, lon):
    return random.randint(1, 100)

def diversity_index(place):
    return round(random.uniform(0.3, 0.9), 2)

def pet_score(green_count, walk_score):
    return round((green_count * 10 + walk_score) / 2)

def parking_score(lat, lon):
    parks = get_nearby_places(lat, lon, 'amenity=parking', 'parking')
    return len(parks)

def get_all_metrics(place, lat, lon):
    housing = avg_housing_cost(place)
    crime = crime_rate(place)
    schools = get_school_data(lat, lon)
    commute_sc, commute_type = commute_score(place)
    parks = get_nearby_places(lat, lon, 'leisure=park', 'parks')
    walk_sc = walkability_score(lat, lon)
    gyms = get_nearby_places(lat, lon, 'leisure=fitness_centre', 'gyms')
    shopping = get_nearby_places(lat, lon, 'shop', 'shopping')
    hospitals = get_nearby_places(lat, lon, 'amenity=hospital', 'hospitals')
    parking_ct = parking_score(lat, lon)
    div_ix = diversity_index(place)
    pet_sc = pet_score(len(parks), walk_sc)

    return {
        "Average Rent (2 bed)": housing['avg_rent_2bed'],
        "Average Sale Price (2 bed)": housing['avg_price_2bed'],
        "Crime Rate": crime,
        "Schools Nearby": [f"{s['name']} (Rating: {s['rating']}, Grades: {s['gradeRange']}, Type: {s['type']})" for s in schools],
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

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_ai(question, context):
    prompt = f"""You are a helpful assistant. Based on the following neighborhood data, answer the user’s question concisely:

{context}

Question: {question}
Answer:"""

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=200,
            n=1,
            stop=None,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        show_error(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process your request right now."

# 🧭 Streamlit UI Setup
st.set_page_config(page_title="Neighborhood Insights", layout="centered")
st.title("Where to live next?")

mode = st.radio("Mode:", ("Compare Two Places", "Single Place"))
place1 = st.text_input("Place 1 (City, State)", "Cambridge, MA")
place2 = st.text_input("Place 2 (City, State)", "Somerville, MA") if mode == "Compare Two Places" else None

if st.button("Show Insights"):
    st.write("Starting geocoding...")
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

    st.write("Geocoding done.")
    locs = [{'lat': lat1, 'lon': lon1, 'place': place1}]
    if mode == "Compare Two Places":
        locs.append({'lat': lat2, 'lon': lon2, 'place': place2})

    st.map(pd.DataFrame(locs))

    st.write("Fetching neighborhood metrics...")
    data1 = get_all_metrics(place1, lat1, lon1)
    data2 = get_all_metrics(place2, lat2, lon2) if mode == "Compare Two Places" else None
    st.write("Metrics fetched.")

    if mode == "Compare Two Places":
        col1, col2 = st.columns(2)
        for col, place, data in [(col1, place1, data1), (col2, place2, data2)]:
            with col:
                st.subheader(place)
                for k, v in data.items():
                    if isinstance(v, list):
                        st.markdown(f"**{k}:**")
                        for item in v:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{k}:** {v}")
    else:
        st.subheader(place1)
        for k, v in data1.items():
            if isinstance(v, list):
                st.markdown(f"**{k}:**")
                for item in v:
                    st.markdown(f"- {item}")
            else:
                st.markdown(f"**{k}:** {v}")

    # --- AI Search Bar ---
    st.markdown("---")
    st.header("Ask the Neighborhood Insights Bot")
    user_question = st.text_input("Ask a question about these neighborhoods:")

    if user_question:
        context = ""
        for place, data in [(place1, data1), (place2, data2) if data2 else (None, None)]:
            if place and data:
                context += f"\nNeighborhood: {place}\n"
                for k, v in data.items():
                    if isinstance(v, list):
                        context += f"{k}: {', '.join(v)}\n"
                    else:
                        context += f"{k}: {v}\n"

        answer = ask_ai(user_question, context)
        st.markdown(f"**Answer:** {answer}")
