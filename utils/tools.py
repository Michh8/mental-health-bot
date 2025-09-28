import requests
import random
import logging
from langchain.tools import Tool

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
        return "😢 Parece que te sientes triste. Te sugiero respirar profundamente 5 veces y dar un pequeño paseo."
    if "estresado" in description or "ansioso" in description:
        return "😰 Parece que estás estresado. Intenta meditar o escuchar música relajante durante 5-10 minutos."
    if "feliz" in description or "bien" in description:
        return "😄 Me alegra que te sientas bien. Mantén esa energía positiva y sigue cuidándote."
    return "💬 Gracias por compartir cómo te sientes. Recuerda que siempre puedes buscar ayuda profesional si lo necesitas."

mood_tool = Tool(
    name="MoodCheckTool",
    description="Analiza brevemente el estado de ánimo y da sugerencias de bienestar.",
    func=mood_check_tool_func
)

# Lista de tools
tools_list = [psych_tool, motivation_tool, mood_tool]
