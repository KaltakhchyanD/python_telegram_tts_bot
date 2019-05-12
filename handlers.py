"""
This module contains handlers used by telegram bot dispatcher at bot.py module.
    
They are:
start_handler - this is called when /start commend is sent to bot
text_handler - this is called when text message is sent to bot
voice_handler - this is called when audio message is sent to bot
"""

from yandex_tts import generate_speech_from_text, generate_text_from_speech


def send_audio(bot, update, user_data, audio_file):
    """ Send audio file to user."""
    with open(audio_file, "rb") as f:
        bot.send_audio(chat_id=update.message.chat_id, audio=f)


def start_handler(bot, update, user_data):
    """Send welcome message to user."""
    text = "Hi! This is Text2Speach test bot"
    update.message.reply_text(text)


def text_handler(bot, update, user_data):
    """Get text from message, generate audio and send it to user."""
    user_text = update.message.text
    update.message.reply_text("Got your text!\nNow i will generate an audio file!")
    audio_file = generate_speech_from_text(user_text)
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
        f"Got your voice! Its duration - {duration} sec, MIME type - {voice.mime_type}"
        + "Now i will generate text from it!"
    )
    text = generate_text_from_speech("audio_from_telegram.ogg")
    update.message.reply_text(text)
