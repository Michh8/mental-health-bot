import os
import logging
import requests
import random
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# LangChain + Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# ===============================
# Configuración inicial
# ===============================
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Validación básica de variables
if not TELEGRAM_TOKEN:
    raise ValueError("❌ Falta TELEGRAM_TOKEN en el archivo .env")
if not GEMINI_API_KEY:
    raise ValueError("❌ Falta GEMINI_API_KEY en el archivo .env")
if not WEATHER_API_KEY:
    raise ValueError("❌ Falta WEATHER_API_KEY en el archivo .env")

# Logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Modelo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GEMINI_API_KEY
)

# ===============================
# Handlers de comandos
# ===============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot.\n\n"
        "Usa /help para ver lo que puedo hacer."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Funcionalidades disponibles:\n\n"
        "/start - Mensaje de bienvenida\n"
        "/help - Mostrar esta ayuda\n"
        "/fecha - Fecha y hora actual\n"
        "/clima [ciudad] - Información meteorológica\n"
        "/motivacion - Mensaje motivacional\n\n"
        "También puedes escribirme cualquier mensaje y te responderé con Gemini 🤖"
    )

async def fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        now = datetime.now()
        dias = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
        meses = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]

        dia_nombre = dias[now.weekday()]           # Monday=0
        mes_nombre = meses[now.month - 1]

        fecha_texto = (
            f"📅 Hoy es {dia_nombre.capitalize()}, {now.day:02d} de {mes_nombre} de {now.year}\n"
            f"🕒 Hora: {now.strftime('%H:%M:%S')}"
        )
        await update.message.reply_text(fecha_texto)
    except Exception as e:
        logging.exception("Error en /fecha")
        await update.message.reply_text("❌ Error al obtener la fecha. Intenta de nuevo.")

async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Usa el formato: /clima [ciudad]\nEjemplo: /clima San Salvador")
        return

    ciudad = " ".join(context.args)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            await update.message.reply_text("⚠️ Ciudad no encontrada. Intenta con otra.")
            return

        nombre = data["name"]
        pais = data["sys"]["country"]
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        hum = data["main"]["humidity"]

        mensaje = (
            f"🌤️ Clima en {nombre}, {pais}:\n"
            f"🌡️ Temperatura: {temp}°C\n"
            f"💧 Humedad: {hum}%\n"
            f"📖 Condición: {desc.capitalize()}"
        )
        await update.message.reply_text(mensaje)

    except Exception as e:
        logging.exception("Error en /clima")
        await update.message.reply_text("❌ Error al obtener el clima, intenta más tarde.")

async def motivacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    frases = [
        "💪 ¡Tú puedes con todo!",
        "🌟 Nunca olvides lo valioso que eres.",
        "🚀 Cada día es una nueva oportunidad.",
        "🔥 No te rindas, lo mejor está por venir."
    ]
    await update.message.reply_text(random.choice(frases))

# ===============================
# Handler de conversación libre con Gemini
# ===============================

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        response = llm.invoke([HumanMessage(content=user_message)])
        await update.message.reply_text(response.content)
    except Exception as e:
        logging.exception("Error en chat Gemini")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar tu mensaje con Gemini.")

# ===============================
# Main
# ===============================

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("fecha", fecha))
    app.add_handler(CommandHandler("clima", clima))
    app.add_handler(CommandHandler("motivacion", motivacion))

    # Chat libre
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot en ejecución...")
    app.run_polling()

if __name__ == "__main__":
    main()
