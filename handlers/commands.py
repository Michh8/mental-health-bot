import logging
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
import requests
from config import WEATHER_API_KEY

# ===============================
# Comandos del bot
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
        dia_nombre = dias[now.weekday()]
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
