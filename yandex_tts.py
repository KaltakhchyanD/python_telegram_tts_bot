import argparse
import json
import os
import requests
import subprocess
import wave

import check_wav_length 

def update_iam_token():

    OauthToken = str(os.getenv('OauthToken'))
    test_string = '{"yandexPassportOauthToken": "'+OauthToken+'"}'
    command = ['curl', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', test_string,  'https://iam.api.cloud.yandex.net/iam/v1/tokens']
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    new_iam_token = json.loads(result.stdout)['iamToken']
    os.environ['IAM_TOKEN'] = new_iam_token


def synthesize_audio(folder_id, iam_token, text):
    url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
    update_iam_token()
    iam_token = os.getenv('IAM_TOKEN')
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


def convert_raw_to_wav(filename):
    source_file = filename
    dest_file = filename.split('.')[0]+"_test.wav"
    with open(filename, 'rb') as raw_file:
        raw_data = raw_file.read()
    with wave.open(dest_file, 'wb') as wav_file:
        wav_file.setparams((1, 2, 48000, 0, 'NONE', 'NONE' ))
        wav_file.writeframes(raw_data)
    return dest_file


def generate_speech_from_text(text):
    folder_id = os.getenv('FOLDER_ID')
    token = os.getenv('IAM_TOKEN')
    output = 'speech.raw'

    audio_content = synthesize_audio(folder_id, token, text)
    with open(output, "wb") as f:
        f.write(audio_content)
    output_file = convert_raw_to_wav('speech.raw')
    return output_file


def prepare_wav(source_file = 'test_voice.wav'):
    dest_file = 'new_test_voice.wav'

    with open(source_file, 'rb') as src_file_wav:
        src_data = src_file_wav.read()

    with wave.open(dest_file, 'wb') as dst_wav_file:
        dst_wav_file.setparams((1, 2, 48000, 0, 'NONE', 'NONE' ))
        dst_wav_file.writeframes(src_data)

    return dest_file


def generate_text_from_speech(source_file):
    folder_id = os.getenv('FOLDER_ID')
    update_iam_token()
    token = os.getenv('IAM_TOKEN')
    voice_file = 'text_from_speach_single.wav'
    #subprocess.call(['opusdec','--rate 48000', '--force-wav', source_file, voice_file])
    print(f'Converted {source_file} to {voice_file}')
    subprocess.call(['sox', source_file, voice_file])
    good_wav_file = prepare_wav(voice_file)
    print(f'Prepared {good_wav_file} from {voice_file} of size {os.path.getsize(good_wav_file)/1024}')
    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

    with open(good_wav_file, 'rb') as f:
        data = f.read()

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    params = {
        'format':'lpcm',
        'sampleRateHertz': 48000,
        'folderId': folder_id
    }

    update_iam_token()
    resp = requests.post( url, params=params, data = data, headers = headers)

    if resp.status_code != 200:
        raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
    return resp.json()['result']


def generate_text_from_long_speech(source_file):
    list_of_texts = []
    subprocess.call(['opusdec','--rate', '48000', '--force-wav', source_file, 'temp_wav_file.wav'])
    #subprocess.call(['sox', source_file, 'temp_wav_file.wav'])
    print(f'Converted {source_file} to temp_wav_file.wav')


    file_size = os.path.getsize('temp_wav_file.wav')/1024
    print(f'File temp_wav_file.wav first size {file_size}')

    prepare_wav('temp_wav_file.wav')
    file_size = os.path.getsize('temp_wav_file.wav')/1024
    print(f'Preparing file temp_wav_file.wav, new size {file_size}')

    if file_size < 1024:
        print('File is small, generating text')
        list_of_texts = [generate_text_from_speech('temp_wav_file.wav')]
        print(f'Generated text of length {len(list_of_texts[0])}')
    else:
        print('File is large, splitting it then generating text')
        list_of_audio_files = check_wav_length.do_the_thing('temp_wav_file.wav')
        print(f'Splitted temp_wav_file.wav into {list_of_audio_files}')
        for file in list_of_audio_files:
            print(f'Generating text from {file}')
            list_of_texts.append(generate_text_from_speech(file))
            print(f'New text length is {len(list_of_texts[-1])}')
    return list_of_texts


def test_from_ogg_to_wav(source_file):
    subprocess.call(['opusdec','--rate', '48000', '--force-wav', source_file, 'convert_with_opusdec.wav'])
    subprocess.call(['sox', source_file, 'convert_with_sox.wav'])

    file_size_opus = os.path.getsize('convert_with_opusdec.wav')/1024
    file_size_sox = os.path.getsize('convert_with_sox.wav')/1024
    print(f'Opusdec size {file_size_opus}')
    print(f'Sox size {file_size_sox}')


if __name__ == "__main__":
    #generate_speech_from_text('Hello world')
    for text in generate_text_from_long_speech('test_voice.ogg'):
        print(text)
    #test_from_ogg_to_wav('test_voice.ogg')









