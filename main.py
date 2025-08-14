from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers=["*"],
)

SPOILERS_ENABLED = False 

@app.post("/toggle_spoilers")
async def toggle_spoilers():
    global SPOILERS_ENABLED
    SPOILERS_ENABLED = not SPOILERS_ENABLED
    return {"spoilers_enabled":SPOILERS_ENABLED}

@app.post("/chat")
async def chat(request:Request):
    data = await request.json()
    user_message = data.get("message","")

    system_prompt = f"""
    You are MovieBot — an AI that ONLY talks about movies, TV shows, and anime.
    Answer clearly and informatively. If asked something outside the scope, politely refuse.
    """

    response = openai.ChatCompletion.create(
        model="gpt-5",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": " user", "content": user_message}
        ],
        temperature=0.8

    )

    bot_reply = response.choices[0].message["content"]
    
    if not SPOILERS_ENABLED:
        Spoiler_prompt = """
        check wheather the following text contains any spoilers. A spoiler is anything that reveals major plot twists, endings, character deaths,
        or other information that would ruin the experience for a first-time viewer. Reply ony with either YES or NO.
        text: {bot_reply}
        """
        check_response = openai.ChatCompletion.create(
            model="gpt-5",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": " user", "content": user_message}
        ],
        temperature=0.6
        )

        Spoiler_prompt = check_response.choices[0].message["content"].strip().upper()
        if Spoiler_prompt == "YES":
            rewrite_prompt = f"""
            Rewrite the following answer so that it avoids giving away any spoilers
            about movies, TV shows, or anime, but still provides a helpful, interesting,
            and engaging response.
            
            Original:
            {bot_reply}
            """
            rewrite_response = openai.ChatCompletion.create(
                model="gpt-5",
                messages=[{"role": "system", "content": rewrite_prompt}],
                temperature=0.7
            )
            safe_answer = rewrite_response.choices[0].message["content"]
            return {"reply": safe_answer}

    
    return {"reply": bot_reply}














