from yandex_tts import generate_speach


def start_handler(bot, update, user_data):
    text = 'Hi! This is Text2Speach test bot'
    update.message.reply_text(text)


def text_handler(bot, update, user_data):
    user_text = update.message.text
    generate_speach(user_text)
    send_audio(bot, update, user_data)


def send_audio(bot, update, user_data):
    with open('speech_new.wav', 'rb') as f:
        bot.send_audio(chat_id=update.message.chat_id, audio=f)


def incomming_audio_handler(bot, update, user_data):
    update.message.reply_text('Got your audio!')


