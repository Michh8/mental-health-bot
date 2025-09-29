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
import google.generativeai as genai  # ✅ Para listar modelos de Gemini
from aiohttp import web  # ✅ Servidor web para mantener vivo el bot

# ===============================
# Verificación de versiones
# ===============================
print("🔍 Verificando entorno...")
print(f"Python versión: {sys.version}")

required = {
    "python-telegram-bot": ">=20.0",
    "langchain-google-genai": ">=0.0.9",
    "python-dotenv": ">=1.0.0",
    "google-generativeai": ">=0.8.3"
}

for package, version in required.items():
    try:
        installed_version = pkg_resources.get_distribution(package).version
        print(f"{package}: {installed_version} (requerido {version})")
    except pkg_resources.DistributionNotFound:
        print(f"⚠ {package} no está instalado")

# ===============================
# Configuración
# ===============================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    print("⚠ GEMINI_API_KEY no está configurada en el .env")

# ===============================
# Modelo Gemini
# ===============================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",  # ✅ Modelo principal
    google_api_key=GEMINI_API_KEY
)

# ===============================
# Chat libre con Gemini
# ===============================
async def chat(update, context):
    try:
        user_message = update.message.text
        response = llm.invoke([HumanMessage(content=user_message)])
        await update.message.reply_text(response.content)
    except Exception as e:
        logging.exception("Error en chat Gemini")
        await update.message.reply_text("⚠ Error al procesar tu mensaje con Gemini.")

# ===============================
# Servidor web para Render / Railway
# ===============================
async def handle(request):
    return web.Response(text="Bot activo ✅")

async def run_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Servidor web corriendo en puerto {port}")
    # Mantener activo mientras el loop viva
    await asyncio.Event().wait()

# ===============================
# Main corregido (polling + webserver)
# ===============================
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("help", commands.help_command))
    app.add_handler(CommandHandler("fecha", commands.fecha))
    app.add_handler(CommandHandler("clima", commands.clima))
    app.add_handler(CommandHandler("motivacion", commands.motivacion))
    app.add_handler(CommandHandler("mood", commands.mood))
    app.add_handler(CommandHandler("centros", commands.centros))

    # Chat libre
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Bot en ejecución...")
    # Ejecutar polling y servidor web en paralelo
    await asyncio.gather(
        app.run_polling(close_loop=False),
        run_webserver()
    )

if _name_ == "_main_":
    asyncio.run(main())

    #probando para commmit 