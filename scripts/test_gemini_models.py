#!/usr/bin/env python3
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

print("사용 가능한 Gemini 모델 목록:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ 모델명: {model.name}")
        print(f"   지원 메서드: {model.supported_generation_methods}")
        print()
