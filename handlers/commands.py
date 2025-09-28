import logging
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from utils.tools import psych_tool, motivation_tool, mood_tool, weather_tool

# ===============================
# Comandos del bot
# ===============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de salud mental.\n\n"
        "Usa /help para ver lo que puedo hacer."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Funcionalidades disponibles:\n\n"
        "/start - Mensaje de bienvenida\n"
        "/help - Mostrar esta ayuda\n"
        "/fecha - Fecha y hora actual\n"
        "/clima [ciudad] - Información meteorológica\n"
        "/motivacion - Mensaje motivacional\n"
        "/mood [describe cómo te sientes] - Comprobación de ánimo\n"
        "/centros [ubicación] - Buscar centros psicológicos cercanos\n\n"
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
        await update.message.reply_text("❗ Usa el formato: /clima [ciudad]")
        return
    ciudad = " ".join(context.args)
    mensaje = weather_tool.func(ciudad)
    await update.message.reply_text(mensaje)

async def motivacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = motivation_tool.func("")
    await update.message.reply_text(mensaje)

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Describe cómo te sientes. Ejemplo: /mood me siento ansioso")
        return
    descripcion = " ".join(context.args)
    mensaje = mood_tool.func(descripcion)
    await update.message.reply_text(mensaje)

async def centros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Indica una ubicación. Ejemplo: /centros San Salvador")
        return
    ubicacion = " ".join(context.args)
    mensaje = psych_tool.func(ubicacion)
    await update.message.reply_text(mensaje)
