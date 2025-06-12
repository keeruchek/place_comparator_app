import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("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")

def ask_openai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

st.set_page_config(page_title="AI Search", layout="centered")

st.title("AI Search Assistant")
question = st.text_input("Ask your question:")

if st.button("Submit") and question:
    with st.spinner("Thinking..."):
        answer = ask_openai(question)
        st.markdown(f"**Answer:** {answer}")
