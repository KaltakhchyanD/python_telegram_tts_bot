from yandex_tts import generate_speech_from_text, generate_text_from_speech, generate_text_from_long_speech


def start_handler(bot, update, user_data):
    text = 'Hi! This is Text2Speach test bot'
    update.message.reply_text(text)


def text_handler(bot, update, user_data):
    user_text = update.message.text
    audio_file = generate_speech_from_text(user_text)
    send_audio(bot, update, user_data, audio_file)


def send_audio(bot, update, user_data, audio_file):
    with open(audio_file, 'rb') as f:
        bot.send_audio(chat_id=update.message.chat_id, audio=f)


def incomming_audio_handler(bot, update, user_data):
    voice = update.message.voice
    voice_id = voice.file_id
    duration = voice.duration
    file_size = voice.file_size

    voice_file = voice.get_file()
    voice_file.download('test_voice.ogg')
    update.message.reply_text(f'Got your voice! Its duration - {duration} sec, MIME type - {voice.mime_type}')
    list_of_text = generate_text_from_long_speech('test_voice.ogg')
    for text in list_of_text:

        update.message.reply_text(text)



