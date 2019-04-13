import argparse
import json
import os
import requests
import subprocess
import wave

import check_wav_length 

def update_iam_token():
    #headers = {
    #    "Content-Type": "application/json"
    #}
    #data = json.dumps({"yandexPassportOauthToken": "AQAAAAAFBe16AATuweFg6nZ8dUXeu0-YIMJuZW8"})
    #print(type(data))
    #print(data)
    #url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    #resp = requests.post(url, headers, data)
    #if resp.status_code!= 200:
    #    print(("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text)))
    #    resp.raise_for_status()
    #    #raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
    #new_iam_token = resp.json()['iamToken']
    #print(new_iam_token)
    OauthToken = str(os.getenv('OauthToken'))
    test_string = '{"yandexPassportOauthToken": "'+OauthToken+'"}'
    command = ['curl', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', test_string,  'https://iam.api.cloud.yandex.net/iam/v1/tokens']
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    #print(result.returncode, result.stdout, result.stderr)
    #print(type(result.stdout))
    #print(result.stdout)
    #print(type(json.loads(result.stdout)))
    #print(json.loads(result.stdout)['iamToken'])
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
    subprocess.call(['opusdec', '--force-wav', source_file, voice_file])
    print(f'Converted {source_file} to {voice_file}')
    #subprocess.call(['sox', source_file, voice_file])
    good_wav_file = prepare_wav(voice_file)
    print(f'Prepared {good_wav_file} from {voice_file}')
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
    subprocess.call(['opusdec', '--force-wav', source_file, 'temp_wav_file.wav'])
    print(f'Converted {source_file} to temp_wav_file.wav')
    #subprocess.call(['sox', source_file, 'temp_wav_file.wav'])
    file_size = os.path.getsize('temp_wav_file.wav')/1024
    print(f'File {source_file} size {file_size}')
    if  file_size < 1024:
        list_of_texts = [generate_text_from_speech(source_file)]
    else:
        wav_from_ogg = 'text_from_speach.wav' 
        subprocess.call(['sox', source_file, wav_from_ogg])
        list_of_audio_files = check_wav_length.do_the_thing(wav_from_ogg)
        for file in list_of_audio_files:
            list_of_texts.append(generate_text_from_speech(file))
    return list_of_texts


if __name__ == "__main__":
    #generate_speech_from_text('Hello world')
    print(generate_text_from_speech('test_voice.ogg'))










