import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print(f"Using key: {api_key[:10]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.0-flash')

try:
    response = model.generate_content("Say 'Hello' in English.")
    print(f"Response: {response.text.strip()}")
except Exception as e:
    print(f"Error: {e}")
