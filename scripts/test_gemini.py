import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('GEMINI_API_KEY')
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"

referers = [
    "http://localhost:3000",
    "https://k-rank.com",
    "https://k-rank.com/",
    "https://k-rank-c5bad.firebaseapp.com",
    "https://k-rank-c5bad.firebaseapp.com/",
    "https://www.nextidealab.com",
    "http://localhost",
    "",
]

data = {"contents": [{"parts": [{"text": "Hello"}]}]}

for r in referers:
    headers = {"Content-Type": "application/json"}
    if r:
        headers["Referer"] = r
    response = requests.post(url, headers=headers, json=data)
    print(f"Referer: '{r}' -> Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS! Use this referer:", r)
        break
