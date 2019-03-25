
def start_handler(bot, update, user_data):
    text = 'Hi! This is Text2Speach test bot'
    update.message.reply_text(text)


def text_handler(bot, update, user_data):
    user_text = update.message.text
    update.message.reply_text(user_text.upper())