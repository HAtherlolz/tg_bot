from telegram.ext import ApplicationBuilder, Updater, MessageHandler, filters

from cfg.config import settings
from services.bot import Bot


def main():
    app = ApplicationBuilder().token(settings.TG_TOKEN).build()

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, Bot.handle_message)
    app.add_handler(message_handler)

    app.run_polling()


if __name__ == '__main__':
    main()
