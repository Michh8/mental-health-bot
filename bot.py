#!/usr/bin/env python3
# bot.py - versión Render-friendly y completa con handlers

import os
import sys
import asyncio
import logging
import signal
from dotenv import load_dotenv
from aiohttp import web

# telegram / langchain / google generative
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
# intenta usar handlers externos si los tienes
try:
    from handlers import commands as custom_handlers
except Exception:
    custom_handlers = None

# langchain-google-genai wrapper (tu dependencia)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import google.generativeai as genai

# importlib.metadata en lugar de pkg_resources
try:
    from importlib.metadata import version, PackageNotFoundError
except Exception:
    version = lambda pkg: None
    PackageNotFoundError = Exception

# ---------- Config y logging ----------
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.environ.get("PORT", 10000))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

print("🔍 Verificando entorno...")
print("Python:", sys.version.splitlines()[0])
for pkg in ("python-telegram-bot", "langchain-google-genai", "python-dotenv", "google-generativeai", "aiohttp"):
    try:
        print(f"{pkg}: {version(pkg)}")
    except PackageNotFoundError:
        print(f"⚠️ {pkg} no está instalado")

# ---------- Conexión a Gemini (opcional) ----------
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("✅ GEMINI configurado. (lista de modelos omitida en logs para brevedad)")
    except Exception as e:
        print("❌ Error al configurar GEMINI:", e)
else:
    print("⚠️ GEMINI_API_KEY no configurada; funcionalidades LLM quedarán limitadas.")

# Crea el wrapper LLM (si no lo usas, está bien)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=GEMINI_API_KEY)

# ---------- Handlers (usa handlers.commands si existe, sino los define aquí) ----------
if custom_handlers:
    # Se asume que custom_handlers exporta funciones: start, help_command, fecha, clima, motivacion, mood, centros
    def attach_custom_handlers(app: Application):
        # handlers obligatorios/frecuentes
        try:
            app.add_handler(CommandHandler("start", custom_handlers.start))
        except Exception:
            logger.debug("No hay start en custom handlers")
        try:
            app.add_handler(CommandHandler("help", custom_handlers.help_command))
        except Exception:
            logger.debug("No hay help_command en custom handlers")
        # opcionales
        for name in ("fecha", "clima", "motivacion", "mood", "centros"):
            if hasattr(custom_handlers, name):
                app.add_handler(CommandHandler(name, getattr(custom_handlers, name)))
else:
    # Handlers por defecto (si no tienes handlers/custom_handlers definidos)
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("¡Hola! 🤖 Bot en Render. Usa /help para ver comandos.")

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Comandos disponibles: /start /help /fecha /clima /motivacion /mood /centros")

    async def fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
        from datetime import datetime
        await update.message.reply_text(f"Fecha y hora actuales: {datetime.utcnow().isoformat()} UTC")

    async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Funcionalidad de clima no configurada. Agrega tu implementación.")

    async def motivacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Eres capaz de todo 💪")

    async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Estado de ánimo: estable :)")

    async def centros(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Centros: información no configurada.")

    def attach_custom_handlers(app: Application):
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("fecha", fecha))
        app.add_handler(CommandHandler("clima", clima))
        app.add_handler(CommandHandler("motivacion", motivacion))
        app.add_handler(CommandHandler("mood", mood))
        app.add_handler(CommandHandler("centros", centros))


# ---------- Handler de chat libre (usa Gemini/langchain) ----------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = (update.message.text or "").strip()
    if not user_text:
        await update.message.reply_text("No recibí texto.")
        return
    # Ejecutar la llamada a llm en un thread para no bloquear
    try:
        response = await asyncio.to_thread(lambda: llm.invoke([HumanMessage(content=user_text)]))
        text = getattr(response, "content", None) or str(response)
        # A veces la API devuelve un objeto con .content o .text; defensivo:
        if hasattr(response, "content"):
            text = response.content if response.content else str(response)
        await update.message.reply_text(text)
    except Exception as e:
        logger.exception("Error llamando al LLM:")
        await update.message.reply_text("⚠️ Error procesando tu mensaje (LLM).")

# ---------- Servidor web para healthchecks ----------
async def handle_root(request):
    return web.Response(text="Bot activo ✅")

async def run_webserver(stop_event: asyncio.Event):
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("🌐 Webserver escuchando en puerto %s", PORT)
    try:
        await stop_event.wait()
    finally:
        logger.info("🔻 Deteniendo webserver...")
        await runner.cleanup()

# ---------- Main (coordina run_polling en hilo y webserver) ----------
async def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("❌ TELEGRAM_TOKEN no configurado en .env o variables de entorno")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Adjunta handlers (propios o fallback)
    attach_custom_handlers(app)

    # Handler de chat libre (último)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Evento para coordinar shutdown del webserver
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    # Ejecutar run_polling() en un hilo para evitar choque con el loop principal
    polling_task = asyncio.create_task(asyncio.to_thread(app.run_polling))

    # Ejecutar webserver en la coroutine principal
    web_task = asyncio.create_task(run_webserver(stop_event))

    # Registro de señales para apagar ordenadamente
    def _shutdown_signal():
        logger.info("🔔 Señal de apagado recibida, iniciando shutdown...")
        if not stop_event.is_set():
            stop_event.set()
        # programar shutdown del bot (coroutine)
        try:
            asyncio.create_task(app.shutdown())
        except Exception as e:
            logger.debug("No se pudo programar app.shutdown(): %s", e)

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown_signal)
        except NotImplementedError:
            # Windows u otros entornos sin add_signal_handler
            pass

    logger.info("🤖 Bot + Webserver arrancando (Render-friendly).")

    # Esperar hasta que una tarea falle o termine
    done, pending = await asyncio.wait(
        {polling_task, web_task}, return_when=asyncio.FIRST_EXCEPTION
    )

    # Si alguna terminó con excepción, propagarla para verla en logs
    for t in done:
        if t.cancelled():
            continue
        exc = t.exception()
        if exc:
            # Asegurar que el bot haga shutdown ordenado antes de salir
            logger.exception("Tarea finalizó con excepción:")
            # Intentamos apagar app limpio
            try:
                await app.shutdown()
            except Exception:
                logger.debug("app.shutdown() falló durante manejo de excepción")
            raise exc

    # Si llegamos aquí normalmente, se está apagando por signal:
    logger.info("✅ Esperando cierre ordenado de tareas...")
    # Cancela pendientes
    for t in pending:
        try:
            t.cancel()
        except Exception:
            pass

    # Asegurar que el bot se apague correctamente
    try:
        await app.shutdown()
    except Exception:
        logger.debug("app.shutdown() lanzó durante apagado final")

    logger.info("Salida completa. Bye.")

# ---------- Entrypoint ----------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        # Log y raise para que Render lo capture en los logs
        logger.exception("Exception en main():")
        raise
