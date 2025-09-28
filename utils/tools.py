import requests
import random
import logging
from langchain.tools import Tool
from config import WEATHER_API_KEY

# ===============================
# Tool 1: Buscar centros psicológicos
# ===============================
def find_psych_centers(location: str) -> str:
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": f"centro psicológico {location}",
            "format": "json",
            "limit": 5
        }
        headers = {"User-Agent": "TelegramBotSaludMental/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=8)
        results = response.json()

        if not results:
            return f"No encontré centros psicológicos cerca de '{location}'."

        output = []
        for r in results:
            name = r.get("display_name", "Desconocido")
            lat = r.get("lat")
            lon = r.get("lon")
            output.append(f"• {name} - 📍 Lat: {lat}, Lon: {lon}")

        return "\n".join(output)

    except Exception as e:
        logging.exception("Error en PsychCentersTool")
        return f"Error al consultar centros psicológicos: {e}"

psych_tool = Tool(
    name="PsychCentersTool",
    description="Busca centros psicológicos cercanos a una ubicación usando OpenStreetMap.",
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
    description = description.lower()
    if "triste" in description or "deprimido" in description:
        return "😢 Parece que te sientes triste. Respira profundamente y da un pequeño paseo."
    if "estresado" in description or "ansioso" in description:
        return "😰 Parece que estás estresado. Medita o escucha música relajante unos minutos."
    if "feliz" in description or "bien" in description:
        return "😄 Me alegra que te sientas bien. Mantén esa energía positiva."
    return "💬 Gracias por compartir cómo te sientes. Recuerda que siempre puedes buscar ayuda profesional si lo necesitas."

mood_tool = Tool(
    name="MoodCheckTool",
    description="Analiza brevemente el estado de ánimo y da sugerencias de bienestar.",
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
        return f"❌ Error al obtener el clima: {e}"

weather_tool = Tool(
    name="WeatherTool",
    description="Obtiene clima de una ciudad",
    func=weather_tool_func
)

# Lista de todas las tools
tools_list = [psych_tool, motivation_tool, mood_tool, weather_tool]
