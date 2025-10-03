import os
import sys
import logging
import importlib.metadata
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import commands
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from utils.tools import tools_list
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
    "google-generativeai": ">=0.8.3"
}

for package, version in required.items():
    try:
        installed_version = importlib.metadata.version(package)
        print(f"{package}: {installed_version} (requerido {version})")
    except importlib.metadata.PackageNotFoundError:
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
    model="gemini-2.5-pro",
    google_api_key=GEMINI_API_KEY
)

# ===============================
# Agent de LangChain usando tus tools
# ===============================
agent = initialize_agent(
    tools_list,  # ✅ Tus tools importadas desde tools.py
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# ===============================
# Chat libre con Agent
# ===============================
async def chat(update, context):
    try:
        user_message = update.message.text
        # Ejecutar el Agent en lugar del llm directo
        response = agent.run(user_message)
        await update.message.reply_text(response)
    except Exception as e:
        logging.exception("Error en chat con Agent")
        await update.message.reply_text("⚠ Error al procesar tu mensaje. Intenta de nuevo.")

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

# ===============================
# Main (polling + webserver)
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

    # Iniciar bot sin bloquear el loop
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Ejecutar servidor web
    await run_webserver()

    # Mantener activo hasta que lo paren
    await asyncio.Event().wait()

    # Cerrar limpieza
    await app.updater.stop()
    await app.stop()
    await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
