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
# Verificación de versiones
# ===============================
print("🔍 Verificando entorno...")
print(f"Python versión: {sys.version}")

required = {
    "python-telegram-bot": ">=20.0",
    "langchain-google-genai": ">=0.0.9",
    "python-dotenv": ">=1.0.0",
    "google-generativeai": ">=0.8.3",
    "aiohttp": ">=3.8.0"
}

for package, version in required.items():
    try:
        installed_version = pkg_resources.get_distribution(package).version
        print(f"{package}: {installed_version} (requerido {version})")
    except pkg_resources.DistributionNotFound:
        print(f"⚠️ {package} no está instalado")

# ===============================
# Configuración
# ===============================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.environ.get("PORT", 10000))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===============================
# Conexión a Gemini
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
    print("⚠️ GEMINI_API_KEY no está configurada en .env")

# ===============================
# Modelo Gemini
# ===============================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=GEMINI_API_KEY
)

# ===============================
# Chat libre con Gemini (async-safe)
# ===============================
async def chat(update, context):
    try:
        user_message = update.message.text
        # Ejecutar invoke de Gemini en un thread para no bloquear el loop
        response = await asyncio.to_thread(lambda: llm.invoke([HumanMessage(content=user_message)]))
        await update.message.reply_text(response.content)
    except Exception:
        logging.exception("Error en chat Gemini")
        await update.message.reply_text("⚠️ Error al procesar tu mensaje con Gemini.")

# ===============================
# Servidor web mínimo (ping)
# ===============================
async def handle(request):
    return web.Response(text="Bot activo ✅")

async def run_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"🌐 Servidor web corriendo en puerto {PORT}")
    while True:
        await asyncio.sleep(3600)

# ===============================
# Main async para evitar warnings
# ===============================
async def start_bot():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("❌ TELEGRAM_TOKEN no está configurado en .env")

    # Crear bot
    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Handlers de comandos
    bot_app.add_handler(CommandHandler("start", commands.start))
    bot_app.add_handler(CommandHandler("help", commands.help_command))
    bot_app.add_handler(CommandHandler("fecha", commands.fecha))
    bot_app.add_handler(CommandHandler("clima", commands.clima))
    bot_app.add_handler(CommandHandler("motivacion", commands.motivacion))
    bot_app.add_handler(CommandHandler("mood", commands.mood))
    bot_app.add_handler(CommandHandler("centros", commands.centros))

    # Handler de chat libre
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Ejecutar servidor web paralelo
    asyncio.create_task(run_webserver())

    print("🤖 Bot en ejecución con polling...")
    await bot_app.run_polling()

if __name__ == "__main__":
    asyncio.run(start_bot())
