import os
import unittest
from unittest.mock import patch, Mock


from src.handlers import text_handler, voice_handler, change_lang_to_rus_handler


class TestTextHandler(unittest.TestCase):
    def test_normal_case(self):
        bot = Mock()
        update = Mock()
        user_data = Mock()
        update.message.text = "One two three fore uno dos tres quatro"
        text_handler(bot, update, user_data)
        bot.send_audio.assert_called()


class TestVoiceHandler(unittest.TestCase):
    def test_normal_case(self):
        bot = Mock()
        update = Mock()
        user_data = Mock()
        change_lang_to_rus_handler(bot, update, user_data)
        voice_handler(bot, update, user_data)

        update.message.reply_text.assert_called_with(
            "24(678)910-11-12 13 14 15 16 17 1819 20"
        )
