import logging
import os

import sentry_sdk
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler

from handlers import start_handler, text_handler, voice_handler, conversation
from settings import PROXY

logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
    #                    filename='bot.log'
)

logger = logging.getLogger(__name__)
logger.info("Telegram_tts_bot")

sentry_sdk.init("https://aaa48c902161413c80612b49c2b7897b@sentry.io/1423053")


def main():
    tts_bot = Updater(os.getenv("API_KEY_BOT"), request_kwargs=PROXY)
    dp = tts_bot.dispatcher
    dp.add_handler(conversation)
    tts_bot.start_polling()
    tts_bot.idle()


if __name__ == "__main__":
    main()
