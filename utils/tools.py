import requests
import random
import logging
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from config import WEATHER_API_KEY, GEMINI_API_KEY

# ===============================
# Modelo Gemini para MoodCheck
# ===============================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",  # ✅ Corregido
    google_api_key=GEMINI_API_KEY
)

# ===============================
# Tool 1: Buscar centros psicológicos
# ===============================
def find_psych_centers(location: str) -> str:
    try:
        search_terms = ["psicólogo", "psicóloga", "clínica psicológica", "hospital mental", "psicologo","psicologa","psicologica","psicologico","clinica psicologica","hospital"]
        headers = {"User-Agent": "TelegramBotSaludMental/1.0"}
        all_results = []

        for term in search_terms:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": f"{term} {location}", "format": "json", "limit": 10}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            results = response.json()
            all_results.extend(results)

        seen = set()
        filtered = []
        for r in all_results:
            name = r.get("display_name", "")
            if name not in seen:
                filtered.append(r)
                seen.add(name)

        if not filtered:
            return f"No encontré psicólogos o clínicas en '{location}'. Intenta otra ciudad."

        output = []
        for r in filtered[:10]:
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
    prompt = f"Analiza el estado de ánimo de esta persona y da un consejo breve: '{description}'"
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        logging.exception("Error en MoodCheckTool, usando fallback básico")
        description = description.lower()
        if "triste" in description or "deprimido" in description:
            return "😢 Parece que te sientes triste. Da un pequeño paseo."
        if "estresado" in description or "ansioso" in description:
            return "😰 Estás estresado. Medita o escucha música relajante unos minutos."
        if "feliz" in description or "bien" in description:
            return "😄 Me alegra que te sientas bien. Mantén esa energía positiva."
        return "💬 Gracias por compartir cómo te sientes. Busca ayuda profesional si lo necesitas."

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
