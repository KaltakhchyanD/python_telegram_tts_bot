"""
This module contains handlers used by telegram bot dispatcher at bot.py module.
    
They are:
conversation - instance of ConversationHandler, that contains all internal handlers and internal states.
States are required for handlers to work in appropriate context(for example to separate language change from 
text input to generate speech from it).

There are internal handlers:
start_handler - this is called when /start commend is sent to bot
text_handler - this is called when text message is sent to bot
voice_handler - this is called when audio message is sent to bot
lang_handler - goes to state to change current language of text/speech to recognize 
change_lang_to_eng_handler - changes lang to eng
change_lang_to_rus_handler - changes lang to rus

Internal states are self explainatory
"""
import re

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    RegexHandler,
    ConversationHandler,
    Filters,
)

from yandex_tts import (
    generate_audio_file_from_text,
    generate_text_from_speech,
    change_current_lang,
)


def send_audio(bot, update, user_data, audio_file):
    """ Send audio file to user."""
    with open(audio_file, "rb") as f:
        bot.send_audio(chat_id=update.message.chat_id, audio=f)


def start_handler(bot, update, user_data):
    """Send welcome message to user."""
    text = "Hi! This is Text2Speach test bot"
    update.message.reply_text(text)
    return "default_state"


def text_handler(bot, update, user_data):
    """Get text from message, generate audio and send it to user."""
    user_text = update.message.text
    update.message.reply_text("Got your text!\nNow i will generate an audio file!")
    audio_file = generate_audio_file_from_text(user_text)
    send_audio(bot, update, user_data, audio_file)


def voice_handler(bot, update, user_data):
    """Get audiofile from message, generate text from it and send it back to user."""
    voice = update.message.voice
    voice_id = voice.file_id
    duration = voice.duration
    file_size = voice.file_size

    voice_file = voice.get_file()
    voice_file.download("audio_from_telegram.ogg")
    update.message.reply_text(
        f"Got your voice! Its duration - {duration} sec, MIME type - {voice.mime_type}\n"
        + "Now i will generate text from it!"
    )
    text = generate_text_from_speech("audio_from_telegram.ogg")
    update.message.reply_text(text)


def lang_handler(bot, update, user_data):
    """Set state to change current language of text/speech to recognize """
    keyboard = ReplyKeyboardMarkup([["Eng"], ["Rus"]])
    update.message.reply_text(
        "Choose language of the text you are typing", reply_markup=keyboard
    )
    return "lang_choise_state"


def change_lang_to_eng_handler(bot, update, user_data):
    """Changes lang to eng"""
    update.message.reply_text("Changed lang to eng", reply_markup=ReplyKeyboardRemove())
    change_current_lang("en-US")
    return "default_state"


def change_lang_to_rus_handler(bot, update, user_data):
    """Changes lang to rus"""
    update.message.reply_text("Changed lang to rus", reply_markup=ReplyKeyboardRemove())
    change_current_lang("ru-RU")
    return "default_state"


def help_handler(bot, update):
    update.message.reply_text(
        "Hi! I will help you generate text from speech and visa versa.\n"
        + "To generate speech just send me some text.\n"
        + "If you whant generate text - record or forward me audio message.\n"
        + "To change language - use command /lang.\n"
        + "If something went wrong - try /start commant again"
    )


conversation = ConversationHandler(
    entry_points=[CommandHandler("start", start_handler, pass_user_data=True)],
    states={
        "default_state": [
            MessageHandler(Filters.text, text_handler, pass_user_data=True),
            MessageHandler(Filters.voice, voice_handler, pass_user_data=True),
            CommandHandler("lang", lang_handler, pass_user_data=True),
            CommandHandler("help", help_handler),
        ],
        "lang_choise_state": [
            RegexHandler("^(Eng)$", change_lang_to_eng_handler, pass_user_data=True),
            RegexHandler("^(Rus)$", change_lang_to_rus_handler, pass_user_data=True),
        ],
    },
    fallbacks=[],
)
