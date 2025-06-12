import streamlit as st
import requests

st.title("Neighborhood Insights Bot with AI Search")

question = st.text_input("Ask the AI a question about neighborhoods:")

if st.button("Submit"):
    if question.strip():
        try:
            response = requests.post(
                "http://localhost:8000/ai/search",
                data={"question": question}
            )
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer returned.")
                st.markdown(f"**AI says:** {answer}")
            else:
                st.error(f"API error: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
    else:
        st.warning("Please enter a question.")
