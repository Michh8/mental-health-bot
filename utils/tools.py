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
    model="gemini-2.5-pro",
    google_api_key=GEMINI_API_KEY
)

# ===============================
# Tool 1: Buscar centros psicológicos usando Overpass API
# ===============================
def find_psych_centers(location: str) -> str:
    query = f"""
    [out:json][timeout:10];
    area["name"="{location}"]->.searchArea;
    (
      node["amenity"="psychologist"](area.searchArea);
      way["amenity"="psychologist"](area.searchArea);
      relation["amenity"="psychologist"](area.searchArea);
    );
    out center 10;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data=query, timeout=15)
        data = response.json().get("elements", [])
        if not data:
            return f"No encontré psicólogos en '{location}'. Intenta otra ciudad."
        output = []
        for e in data[:10]:
            name = e.get("tags", {}).get("name", "Desconocido")
            lat = e.get("lat") or e.get("center", {}).get("lat")
            lon = e.get("lon") or e.get("center", {}).get("lon")
            output.append(f"• {name} - 📍 Lat: {lat}, Lon: {lon}")
        return "\n".join(output)
    except Exception as e:
        logging.exception("Error en PsychCentersTool (Overpass)")
        return f"❌ Error al buscar psicólogos en '{location}': {e}"

psych_tool = Tool(
    name="PsychCentersTool",
    description="Busca psicólogos o clínicas psicológicas cercanas a una ubicación usando Overpass API.",
    func=find_psych_centers
)

# ===============================
# Tool 2: Motivación / bienestar
# ===============================
def motivation_tool_func(query: str) -> str:
    prompt = f"""
Eres un asistente de apoyo emocional breve. 
Tu tarea es:
1. Dar un mensaje de motivación cálido y comprensivo.
2. Sugerir una acción práctica para mejorar el bienestar emocional 
   (ej. respirar profundo, escribir un diario, salir a caminar).
3. Si detectas señales de desesperanza extrema o pensamientos de autolesión, 
   responde de forma empática y sugiere buscar ayuda profesional o llamar a una línea de emergencia, 
   sin dar consejos peligrosos.

Usuario: "{query}"
Responde en un tono positivo, breve y en español.
"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        logging.exception("Error en MotivationTool, usando fallback básico")
        frases = [
            "💖 Recuerda que no estás solo/a. Hablar con alguien de confianza puede ayudarte.",
            "🧘 Respira profundo tres veces, eso ayuda a calmar tu mente.",
            "🌟 Cada día trae una nueva oportunidad para avanzar un poquito más."
        ]
        return random.choice(frases)

motivation_tool = Tool(
    name="MotivationTool",
    description="Proporciona mensajes motivacionales personalizados y consejos prácticos de bienestar emocional usando IA.",
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
