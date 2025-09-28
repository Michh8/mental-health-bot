import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN
from handlers import commands, messages

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", commands.start))
    app.add_handler(CommandHandler("help", commands.help_command))
    app.add_handler(CommandHandler("fecha", commands.fecha))
    app.add_handler(CommandHandler("clima", commands.clima))
    app.add_handler(CommandHandler("motivacion", commands.motivacion))

    # Chat libre con agente LangChain
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.chat))

    print("🤖 Bot en ejecución...")
    app.run_polling()

if __name__ == "__main__":
    main()
