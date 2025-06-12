from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("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")

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

@app.get("/")
async def root():
    return {"message": "API is running."}
