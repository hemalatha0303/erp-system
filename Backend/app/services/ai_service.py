import requests
import os
from dotenv import load_dotenv
load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_attendance_advice(low_attendance_data):
    prompt = f"""
    You are an AI assistant inside a college ERP system.

    Attendance issues:
    {low_attendance_data}

    Rules:
    - Minimum attendance is 75%
    - Respond in **max 4 bullet points**
    - Keep it **short and clear**
    - Do NOT write an email or letter
    - No greetings, no sign-off

    Focus on:
    1. Subjects below 75%
    2. How much attendance is short
    3. Immediate action student should take
    """

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent",
        params={"key": GEMINI_API_KEY},
        json={
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
    )

    data = response.json()

    if "candidates" in data:
        return data["candidates"][0]["content"]["parts"][0]["text"]

    if "error" in data:
        return f"AI service error: {data['error']['message']}"

    return "AI advice unavailable."