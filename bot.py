import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import commands
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import google.generativeai as genai

# ===============================
# Configuración
# ===============================
print("🔍 Verificando entorno...")
print(f"Python versión: {sys.version}")

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ej: https://tu-app.onrender.com

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
def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("❌ TELEGRAM_TOKEN no está configurado en .env")

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

    # ==============================
    # OPCIÓN 1: USAR POLLING (desarrollo local)
    # ==============================
    if os.getenv("USE_POLLING", "false").lower() == "true":
        print("▶️ Iniciando bot en modo polling...")
        app.run_polling()
    else:
        # ==============================
        # OPCIÓN 2: USAR WEBHOOK (producción en Render/Railway)
        # ==============================
        if not WEBHOOK_URL:
            raise RuntimeError("❌ Debes definir WEBHOOK_URL en el .env para usar webhook")

        print(f"🤖 Bot en ejecución con webhook en {WEBHOOK_URL}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TELEGRAM_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}",
        )


if __name__ == "__main__":
    main()
