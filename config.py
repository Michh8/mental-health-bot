import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Validación básica
if not TELEGRAM_TOKEN or not GEMINI_API_KEY or not WEATHER_API_KEY or not GOOGLE_MAPS_API_KEY:
    raise ValueError("❌ Falta alguna API key en .env")
