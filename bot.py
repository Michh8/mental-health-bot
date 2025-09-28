import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import commands
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# ===============================
# Configuración
# ===============================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Modelo Gemini
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GEMINI_API_KEY)

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
        await update.message.reply_text("⚠️ Error al procesar tu mensaje con Gemini.")

# ===============================
# Main
# ===============================
def main():
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
    app.run_polling()

if __name__ == "__main__":
    main()
