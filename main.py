from telegram.ext import ApplicationBuilder, MessageHandler, filters

from cfg.config import settings
from services.bot import Bot
from utils.logs import log


def main():
    log.info("Bot starting ...")
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, Bot.handle_message)
    app.add_handler(message_handler)

    log.info("Bot is running and listening")
    app.run_polling()
    log.info("Bot is shut down")


if __name__ == '__main__':
    main()
