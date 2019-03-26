import logging
import os

import sentry_sdk
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from handlers import start_handler, text_handler, incomming_audio_handler
from settings import PROXY

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO
#                    filename='bot.log'
                    )

logger = logging.getLogger(__name__)
logger.info('Telegram_tts_bot')

sentry_sdk.init("https://aaa48c902161413c80612b49c2b7897b@sentry.io/1423053")


def main():
    tts_bot = Updater(os.getenv('API_KEY'), request_kwargs = PROXY)
    dp = tts_bot.dispatcher
    dp.add_handler(CommandHandler('start', start_handler, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, text_handler, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.voice, incomming_audio_handler, pass_user_data=True))


    tts_bot.start_polling()
    tts_bot.idle()







if __name__ == '__main__':
    main()