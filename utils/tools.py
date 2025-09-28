import requests
import random
import logging
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import WEATHER_API_KEY, GEMINI_API_KEY

# Modelo Gemini para MoodCheck
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

# ===============================
# Tool 1: Buscar centros psicológicos
# ===============================
def find_psych_centers(location: str) -> str:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"psicólogo {location}",  # mejora en la query
            "format": "json",
            "limit": 10
        }
        headers = {"User-Agent": "TelegramBotSaludMental/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=8)
        results = response.json()

        if not results:
            return f"No encontré psicólogos o clínicas en '{location}'."

        output = []
        for r in results:
            name = r.get("display_name", "Desconocido")
            lat = r.get("lat")
            lon = r.get("lon")
            output.append(f"• {name} - 📍 Lat: {lat}, Lon: {lon}")

        return "\n".join(output)

    except Exception as e:
        logging.exception("Error en PsychCentersTool")
        return f"Error al consultar psicólogos: {e}"

psych_tool = Tool(
    name="PsychCentersTool",
    description="Busca psicólogos o clínicas psicológicas cercanas a una ubicación usando OpenStreetMap.",
    func=find_psych_centers
)

# ===============================
# Tool 2: Motivación / bienestar
# ===============================
def motivation_tool_func(query: str) -> str:
    frases = [
        "💪 ¡Tú puedes con todo!",
        "🌟 Nunca olvides lo valioso que eres.",
        "🚀 Cada día es una nueva oportunidad.",
        "🔥 No te rindas, lo mejor está por venir.",
        "🧘‍♂️ Respira profundo, todo estará bien.",
        "💖 Tómate un momento para ti y tu bienestar."
    ]
    return random.choice(frases)

motivation_tool = Tool(
    name="MotivationTool",
    description="Proporciona mensajes motivacionales y consejos de bienestar emocional.",
    func=motivation_tool_func
)

# ===============================
# Tool 3: Comprobación de ánimo
# ===============================
def mood_check_tool_func(description: str) -> str:
    """
    Versión avanzada: usa Gemini para análisis de estado de ánimo
    """
    prompt = f"Analiza el estado de ánimo de esta persona y da un consejo breve de bienestar: '{description}'"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        logging.exception("Error en MoodCheckTool")
        return "💬 No pude analizar tu estado de ánimo, pero recuerda cuidar de ti mismo."

mood_tool = Tool(
    name="MoodCheckTool",
    description="Analiza el estado de ánimo con IA y da consejos de bienestar emocional.",
    func=mood_check_tool_func
)

# ===============================
# Tool 4: Clima
# ===============================
def weather_tool_func(ciudad: str) -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return f"⚠️ Ciudad no encontrada: {ciudad}"

        nombre = data["name"]
        pais = data["sys"]["country"]
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        hum = data["main"]["humidity"]

        return (
            f"🌤️ Clima en {nombre}, {pais}:\n"
            f"🌡️ Temperatura: {temp}°C\n"
            f"💧 Humedad: {hum}%\n"
            f"📖 Condición: {desc.capitalize()}"
        )
    except Exception as e:
        logging.exception("Error en WeatherTool")
        return f"❌ Error al obtener el clima: {e}"

weather_tool = Tool(
    name="WeatherTool",
    description="Obtiene clima de una ciudad",
    func=weather_tool_func
)

# ===============================
# Lista de todas las tools
# ===============================
tools_list = [psych_tool, motivation_tool, mood_tool, weather_tool]
