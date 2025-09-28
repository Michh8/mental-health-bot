import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import psych_tool, motivation_tool, mood_tool, weather_tool

# ===============================
# Comandos básicos
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot de Salud Mental👋.\n\n"
        "Usa /help para ver lo que puedo hacer 🤖."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Funcionalidades disponibles:\n\n"
        "/start - Mensaje de bienvenida\n"
        "/help - Mostrar esta ayuda\n"
        "/fecha - Fecha y hora actual\n"
        "/clima [ciudad] - Información meteorológica\n"
        "/motivacion - Mensaje motivacional\n"
        "/mood [cómo te sientes] - Revisa tu estado de ánimo\n"
        "/centros [ciudad] - Buscar psicólogos cercanos\n\n"
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

# ===============================
# Comandos que usan tools
# ===============================
async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Usa el formato: /clima [ciudad]")
        return
    ciudad = " ".join(context.args)
    resultado = weather_tool.run(ciudad)
    await update.message.reply_text(resultado)

async def motivacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resultado = motivation_tool.run("motivacion")
    await update.message.reply_text(resultado)

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Describe cómo te sientes: /mood [tu estado]")
        return
    estado = " ".join(context.args)
    resultado = mood_tool.run(estado)
    await update.message.reply_text(resultado)

async def centros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Usa el formato: /centros [ciudad]")
        return
    ciudad = " ".join(context.args)
    resultado = psych_tool.run(ciudad)
    await update.message.reply_text(resultado)
