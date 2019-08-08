# python_telegram_tts_bot
> Telegram bot that does TTS & STT via Yandex SpeechKit on python

[![Build Status](https://travis-ci.org/KaltakhchyanD/python_telegram_tts_bot.svg?branch=master)](https://travis-ci.org/KaltakhchyanD/python_telegram_tts_bot)
[![Maintainability](https://api.codeclimate.com/v1/badges/6f19a9b8c1e0080f66b9/maintainability)](https://codeclimate.com/github/KaltakhchyanD/python_telegram_tts_bot/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/6f19a9b8c1e0080f66b9/test_coverage)](https://codeclimate.com/github/KaltakhchyanD/python_telegram_tts_bot/test_coverage)
[![Documentation Status](https://readthedocs.org/projects/python-telegram-tts-bot/badge/?version=latest)](https://python-telegram-tts-bot.readthedocs.io/en/latest/?badge=latest)

With this bot written on python3 with python-telegram-bot (<https://github.com/python-telegram-bot/python-telegram-bot>), you can create a bot that converts text message from a user into an audio file and voice message into text.

Take into consideration that it's my pet project.


## Before installation
Bot requires python 3.6+
You have to register your bot at BotFather and create Yandex Cloud account. More on that down below
Also you need to obtain 4 tokens:
 - telegram bot api token (<https://core.telegram.org/bots#6-botfather>)
 - IAM token (<https://cloud.yandex.com/docs/speechkit/concepts/auth>)
 - Folder_ID - id your folder at Yandex Cloud. More on Yandex Cloud (<https://cloud.yandex.com>)
 - Get an OAuth token from Yandex.OAuth. To do this, follow the link (<https://oauth.yandex.com/authorize?response_type=token&client_id=1a6990aa636648e9b2ef855fa7bec2fb>), click Allow and copy the OAuth token that is issued.

This bot uses this tokens as env variables - you should export them locally by yourself with these exact names:

```sh
 export API_KEY_BOT=...
 export IAM_TOKEN=...
 export FOLDER_ID=...
 export OauthToken=...
```

As you may see IAM token works only for 12 hours. This bot will update it automatically so you don't have to worry about it.

## Installation

#### OS X & Linux:

Clone this repo
```sh
 git clone 
```
Install sox and ffmpeg. Sox is used to split audio on silence, ffmpeg - for audio files conversion.

For Linux:
```sh
sudo apt-get install -y sox ffmpeg
```

For OS X:
```sh
brew install sox ffmpeg
```

Create virtual env and install dependencies
```sh
python3 -m venv env
./env/bin/activate
pip install -r requirements.txt
```
Setup required env vars as it was mentioned erlier
 
Run it
```sh
python bot.py
```

## Usage example

There are 4 modules:
 - bot.py - this is top module 
 - handlers.py - contains handlers and conversation for python-telegram-bot dispatcher 
 - yandex_tts(need to rename) - helds funcs to work with Yandex API
 - check_wav_length(definitely need to rename) - contains functions to work with audio files
 
So if you want to change and customize something - go there and change stuff.

P.S. Also I've made readthedocs documentation(<https://python-telegram-tts-bot.readthedocs.io/en/latest/index.html>) but probably I won't support it(I've made it just to test Sphinx and RST)

## Contributing

1. Fork it (<https://github.com/KaltakhchyanD/python_telegram_tts_bot/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[python-telegam-bot]: https://github.com/python-telegram-bot/python-telegram-bot
