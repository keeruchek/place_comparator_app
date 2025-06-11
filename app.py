
from flask import Flask, render_template, request
from utils import get_lat_lon, get_all_metrics, generate_insight_answer
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("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")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    place1 = request.form['place1']
    place2 = request.form['place2']

    lat1, lon1 = get_lat_lon(place1)
    lat2, lon2 = get_lat_lon(place2)

    data1 = get_all_metrics(place1, lat1, lon1)
    data2 = get_all_metrics(place2, lat2, lon2)

    return render_template('compare.html', place1=place1, place2=place2, data1=data1, data2=data2)

@app.route('/ask', methods=['POST'])
def ask():
    question = request.form['question']
    response = generate_insight_answer(question)
    return render_template('ask.html', question=question, response=response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
