import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REAL_ESTATE_API = os.getenv("REAL_ESTATE_API")
SCHOOL_RATING_API = os.getenv("SCHOOL_RATING_API")

def get_lat_lon(place):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={place}"
    res = requests.get(url).json()
    if res:
        return res[0]["lat"], res[0]["lon"]
    return None, None

def get_real_estate_data(place):
    return f"Sample real estate data for {place} from {REAL_ESTATE_API}"

def get_crime_data(lat, lon):
    return f"Sample crime data for ({lat}, {lon})"

def get_nearby_amenities(lat, lon, amenity):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node
      ["amenity"="{amenity}"]
      (around:3000,{lat},{lon});
    out;
    """
    response = requests.post(overpass_url, data={'data': query})
    data = response.json()
    return [el["tags"].get("name", "Unnamed") for el in data.get("elements", [])]

def get_school_ratings(lat, lon):
    url = f"https://api.greatschools.org/schools/nearby?key={SCHOOL_RATING_API}&lat={lat}&lon={lon}&limit=5"
    response = requests.get(url)
    schools = []
    if response.status_code == 200:
        data = response.json()
        for school in data.get("schools", []):
            schools.append({
                "name": school.get("name", "Unknown"),
                "rating": school.get("rating", "N/A"),
                "gradeRange": school.get("gradeRange", ""),
                "type": school.get("type", "")
            })
    return schools

def get_all_metrics(place, lat, lon):
    return {
        "Real Estate": get_real_estate_data(place),
        "Crime Data": get_crime_data(lat, lon),
        "Hospitals Nearby": get_nearby_amenities(lat, lon, "hospital"),
        "Gyms Nearby": get_nearby_amenities(lat, lon, "gym"),
        "Grocery Stores Nearby": get_nearby_amenities(lat, lon, "supermarket"),
        "Schools Nearby": [f"{s['name']} (Rating: {s['rating']}, Grades: {s['gradeRange']}, Type: {s['type']})" for s in get_school_ratings(lat, lon)],
    }

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        place1 = request.form["place1"]
        place2 = request.form["place2"]
        lat1, lon1 = get_lat_lon(place1)
        lat2, lon2 = get_lat_lon(place2)

        if not lat1 or not lat2:
            return render_template("index.html", error="Unable to locate one or both places.")

        data1 = get_all_metrics(place1, lat1, lon1)
        data2 = get_all_metrics(place2, lat2, lon2)

        return render_template("index.html", data1=data1, data2=data2, place1=place1, place2=place2)

    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json.get("query", "")
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": user_query}]
    }
    res = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
    answer = res.json()["choices"][0]["message"]["content"]
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
