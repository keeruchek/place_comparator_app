import os
import pandas as pd
import streamlit as st
import requests
import random
import openai

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

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

# Nearby places via Overpass API
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
        data = response.json()
        places = []
        for element in data.get("elements", []):
            name = element.get("tags", {}).get("name")
            if name:
                places.append(name)
        return places[:10] if places else [f"No {label} found"]
    except Exception as e:
        return [f"Error fetching {label}: {e}"]

def avg_housing_cost(place):
    # Simulate average rent and sale price for 2-bedroom
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
    # Mock example with fixed data since no API key access
    # In production, replace with API call to school rating source
    return [
        {'name': 'Lincoln Elementary', 'rating': 8, 'gradeRange': 'K–5', 'type': 'Public', 'address': '123 Lincoln St'},
        {'name': 'Washington High School', 'rating': 7, 'gradeRange': '9–12', 'type': 'Public', 'address': '456 Washington Ave'},
        {'name': 'St. Mary\'s Academy', 'rating': 9, 'gradeRange': '6–8', 'type': 'Private', 'address': '789 Mary Blvd'},
    ]

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

def format_metrics_for_ai(data, place_name):
    lines = [f"Neighborhood data for {place_name}:"]
    for k, v in data.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"- {item}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)

def query_openai(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7,
            n=1,
            stop=None,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

# 🧭 Streamlit UI Setup
st.set_page_config(page_title="Neighborhood Insights", layout="centered")
st.title("Where to live next?")

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
    locs = [{'lat': lat1, 'lon': lon1, 'place': place1}]
    if mode == "Compare Two Places":
        locs.append({'lat': lat2, 'lon': lon2, 'place': place2})
    st.map(pd.DataFrame(locs))

    data1 = get_all_metrics(place1, lat1, lon1)
    data2 = get_all_metrics(place2, lat2, lon2) if mode == "Compare Two Places" else None

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

    # ===== AI Search Bar Section =====
    st.markdown("---")
    st.header("Ask AI about these neighborhoods")

    user_question = st.text_input("Enter your question here:")
    if user_question:
        # Prepare context for AI with neighborhood data summaries
        context_parts = []
        context_parts.append(format_metrics_for_ai(data1, place1))
        if mode == "Compare Two Places":
            context_parts.append(format_metrics_for_ai(data2, place2))
        context = "\n\n".join(context_parts)

        # Combine context and question into prompt
        prompt = f"""You are a helpful assistant knowledgeable about neighborhoods. Use the following neighborhood data to answer the user's question clearly and concisely.

{context}

Question: {user_question}

Answer:"""

        answer = query_openai(prompt)
        st.markdown(f"**Answer:** {answer}")
