import requests
import google.generativeai as genai
from dotenv import load_dotenv
import os
GEMINI_API_KEY = ""
genai.configure(api_key=GEMINI_API_KEY)

model_name = "models/gemini-2.0-flash-lite"
model = genai.GenerativeModel(model_name=model_name)
response = model.generate_content("generate 100 baby boy names")

print(response.text)