
import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import commands  # 👈 tus handlers personalizados
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import google.generativeai as genai
from aiohttp import web

# ===============================
# Logging
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ===============================
# Cargar variables de entorno
# ===============================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    logger.error("❌ No se encontró BOT_TOKEN en el entorno")
    sys.exit(1)

if not GEMINI_API_KEY:
    logger.warning("⚠️ No se encontró GEMINI_API_KEY en el entorno")

# ===============================
# Inicializar Gemini
# ===============================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=GEMINI_API_KEY)
    logger.info("✅ GEMINI configurado.")
else:
    llm = None

# ===============================
# Handlers de ejemplo base
# ===============================
async def start(update, context):
    await update.message.reply_text("Hola 👋 Soy tu bot con aiohttp + Telegram 🤖")

async def echo(update, context):
    text = update.message.text
    await update.message.reply_text(f"Me dijiste: {text}")

# ===============================
# Configuración de Telegram Bot
# ===============================
async def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers base
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Handlers personalizados (mantengo los tuyos 👇)
    commands.register_handlers(app)

    # Inicializar sin run_polling()
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("🤖 Bot de Telegram corriendo con polling...")

# ===============================
# Servidor aiohttp
# ===============================
async def run_web():
    async def health(request):
        return web.Response(text="✅ Servidor aiohttp activo")

    web_app = web.Application()
    web_app.router.add_get("/", health)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logger.info("🌐 Servidor aiohttp iniciado en puerto 8080")

# ===============================
# Main
# ===============================
async def main():
    await asyncio.gather(run_bot(), run_web())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error al iniciar: {e}", exc_info=True)

