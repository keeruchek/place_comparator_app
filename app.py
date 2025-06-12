from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with actual domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/ai/search")
async def ai_search(question: str = Form(...)):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=200
        )
        answer = response['choices'][0]['message']['content']
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        return JSONResponse(content={"answer": f"Error: {str(e)}"}, status_code=500)

# Your existing source code goes below this line
# --------------------------------------------------

# Example placeholder: add your existing Streamlit or other routes here
# If you had another app object, make sure to merge routes properly

@app.get("/")
async def root():
    return {"message": "Main app is running."}
