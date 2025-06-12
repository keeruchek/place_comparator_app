import openai
import os

openai.api_key = os.getenv("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")

def ask_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"OpenAI API Error: {e}"
