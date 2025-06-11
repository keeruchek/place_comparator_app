import os
from flask import Flask, request, render_template, jsonify
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route('/ai')
def ai_form():
    return render_template("ai_search.html")

@app.route('/ai/search', methods=['POST'])
def ai_search():
    question = request.form.get("question", "")
    if not question:
        return jsonify({"answer": "Please enter a question."})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a helpful assistant that answers user questions."},
                {"role": "user", "content": question}
            ]
        )
        answer = response["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
