'''
bot.py
------
Main module of this bot
'''


import logging
import os

import sentry_sdk
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)

from handlers import start_handler, text_handler, voice_handler, conversation
from settings import PROXY

logging.basicConfig(
    format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename='bot.log'
)

logger = logging.getLogger(__name__)
logger.info("Telegram_tts_bot")

sentry_sdk.init("https://aaa48c902161413c80612b49c2b7897b@sentry.io/1423053")

def error_handler(bot, update, error):
    try:
        raise error
    except Unauthorized:
        logger.exception("There was an Unauthorized exception ")
        # remove update.message.chat_id from conversation list
    except BadRequest:
        logger.exception("There was an BadRequest exception ")
        # handle malformed requests - read more below!
    except TimedOut:
        logger.exception("There was an TimedOut exception ")
        # handle slow connection problems
    except NetworkError:
        logger.exception("There was an NetworkError exception ")
        # handle other connection problems
    except ChatMigrated as e:
        logger.exception("There was an ChatMigrated exception ")
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        logger.exception("There was some generic TelegramError exception ")
        # handle all other telegram related errors


def main():
    '''
    This is a main function of bot.py module
    '''
    tts_bot = Updater(os.getenv("API_KEY_BOT"), request_kwargs=PROXY)
    dp = tts_bot.dispatcher
    dp.add_handler(conversation)
    dp.add_error_handler(error_handler)
    tts_bot.start_polling()
    tts_bot.idle()


if __name__ == "__main__":
    main()
