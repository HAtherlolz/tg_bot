from telegram.ext import ApplicationBuilder, MessageHandler, filters

from cfg.config import settings
from cfg.database import ping_db
from services.bot import Bot
from utils.logs import log


def main():
    ping_db()  # checking if db is running

    log.info("Bot is starting ...")
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, Bot.handle_message)
    app.add_handler(message_handler)

    log.info("Bot is running and listening")
    app.run_polling()
    log.info("Bot is shut down")


if __name__ == '__main__':
    main()
