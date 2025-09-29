import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# ========================
# Configuración básica
# ========================
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ========================
# Handlers
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! 🤖 Estoy vivo en Render.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

# ========================
# Main
# ========================
def main():
    if not TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN no está definido en .env o Render")

    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))

    # Mensajes normales
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # 🚀 Importante: solo esto, sin asyncio.run
    app.run_polling()

if __name__ == "__main__":
    main()
