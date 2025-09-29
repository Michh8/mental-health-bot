import os
import sys
import logging
import pkg_resources
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import commands
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import google.generativeai as genai
from aiohttp import web

# ===============================
# Configuración
# ===============================
print("🔍 Verificando entorno...")
print(f"Python versión: {sys.version}")

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ej: https://tu-app.onrender.com/webhook

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===============================
# Probar conexión con Gemini
# ===============================
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("\n✅ Conectado a Gemini correctamente. Modelos disponibles:")
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(" -", m.name)
    except Exception as e:
        print("❌ Error al conectar con Gemini:", e)
else:
    print("⚠️ GEMINI_API_KEY no está configurada en el .env")

# ===============================
# Modelo Gemini
# ===============================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=GEMINI_API_KEY
)

# ===============================
# Handlers
# ===============================
async def chat(update, context):
    try:
        user_message = update.message.text
        response = llm.invoke([HumanMessage(content=user_message)])
        await update.message.reply_text(response.content)
    except Exception:
        logging.exception("Error en chat Gemini")
        await update.message.reply_text("⚠️ Error al procesar tu mensaje con Gemini.")

# ===============================
# Main con Webhook
# ===============================
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("help", commands.help_command))
    app.add_handler(CommandHandler("fecha", commands.fecha))
    app.add_handler(CommandHandler("clima", commands.clima))
    app.add_handler(CommandHandler("motivacion", commands.motivacion))
    app.add_handler(CommandHandler("mood", commands.mood))
    app.add_handler(CommandHandler("centros", commands.centros))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Servidor aiohttp para recibir webhook
    web_app = web.Application()
    web_app.router.add_post("/webhook", app.webhook_handler)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    # Configurar webhook en Telegram
    await app.bot.set_webhook(url=WEBHOOK_URL)

    print(f"🤖 Bot en ejecución con webhook en {WEBHOOK_URL}")
    await asyncio.Event().wait()  # mantiene el proceso vivo


if __name__ == "__main__":
    asyncio.run(main())
