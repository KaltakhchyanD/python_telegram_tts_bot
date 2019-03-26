import argparse
import os
import requests
import subprocess
import wave


def synthesize(folder_id, iam_token, text):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    headers = {
        'Authorization': 'Bearer ' + iam_token,
    }

    data = {
        'text': text,
        'lang': 'en-US',
        'folderId': folder_id,
        'format': 'lpcm',
        'sampleRateHertz': 48000,
    }

    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code != 200:
        raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

    return resp.content


def generate_speach(text):
    folder_id = os.getenv('FOLDER_ID')
    token = os.getenv('IAM_TOKEN')
    output = 'speech.raw'

    audio_content = synthesize(folder_id, token, text)
    with open(output, "wb") as f:
        f.write(audio_content)
    convert_raw_to_wav('speech.raw')
    #subprocess.call(['sox', '-r', '48000', '-b', '16', '-e', 'signed-integer', '-c', '1', 'speech.raw', 'speech.wav'])


def convert_raw_to_wav(filename):
    source_file = filename
    dest_file = filename.split('.')[0]+"_new.wav"
    with open(filename, 'rb') as raw_file:
        raw_data = raw_file.read()
    with wave.open(dest_file, 'wb') as wav_file:
        wav_file.setparams((1, 2, 48000, 0, 'NONE', 'NONE' ))
        wav_file.writeframes(raw_data)

if __name__ == "__main__":
    generate_speach('Hello world')