import os
import openai
import requests
import pandas as pd
import random

openai.api_key = os.getenv("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")

def get_lat_lon(place):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    resp = requests.get(url, params=params, timeout=10).json()
    if resp:
        return float(resp[0]["lat"]), float(resp[0]["lon"])
    return None, None

def get_nearby_places(lat, lon, key, value, radius=1500):
    # Reuse your existing Overpass logic here...
    # Return list of place names
    return []

def get_all_metrics(place, lat, lon):
    # Use your existing get_all_metrics code block
    return {
        "Example Metric": "Value"
        # Populate more metrics...
    }

def generate_insight_answer(question):
    prompt = f"You are a helpful AI assistant answering questions about neighborhoods. Q: {question} A:"
    try:
        resp = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        return resp.choices[0].text.strip()
    except Exception as e:
        return f"Error generating AI answer: {e}"
