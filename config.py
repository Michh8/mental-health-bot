import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("❌ Falta TELEGRAM_TOKEN en el archivo .env")
if not GEMINI_API_KEY:
    raise ValueError("❌ Falta GEMINI_API_KEY en el archivo .env")
if not WEATHER_API_KEY:
    raise ValueError("❌ Falta WEATHER_API_KEY en el archivo .env")
