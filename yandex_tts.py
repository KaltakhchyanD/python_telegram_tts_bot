"""
This module contains provides ability to perform TTS and STT with Yandex TTS and STT services.

It contains these functions:
generate_speech_from_text() - returns wav audio synthesized from input text
generate_text_from_long_speech() - returns text generated from input ogg audio
"""

import argparse
import json
import os
import requests
import subprocess
import wave

import check_wav_length


def update_iam_token():
    """
    Update IAM token and update env var of it.

    Get OauthToken from env var
    Get IAM token with curl using subprocess
    Update IAM token env var
    """

    OauthToken = str(os.getenv("OauthToken"))
    OauthToken_string = '{"yandexPassportOauthToken": "' + OauthToken + '"}'
    command = [
        "curl",
        "-X",
        "POST",
        "-H",
        "Content-Type: application/json",
        "-d",
        OauthToken_string,
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
    ]

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    new_iam_token = json.loads(result.stdout)["iamToken"]
    os.environ["IAM_TOKEN"] = new_iam_token


def synthesize_audio(folder_id, iam_token, text):
    """
    Send text to Yandex TTS and return audio content from response.

    Update IAM token with update_iam_token()
    Send POST request to Yandex TTS service
    Return synthersized audio content from response
    """

    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    update_iam_token()
    iam_token = os.getenv("IAM_TOKEN")
    headers = {"Authorization": "Bearer " + iam_token}

    data = {
        "text": text,
        "lang": "en-US",
        "folderId": folder_id,
        "format": "lpcm",
        "sampleRateHertz": 48000,
    }
    resp = requests.post(url, headers=headers, data=data)

    if resp.status_code != 200:
        raise RuntimeError(
            "Invalid response received: code: %d, message: %s"
            % (resp.status_code, resp.text)
        )

    return resp.content


def convert_raw_to_wav(filename):
    """
    Read source raw file and write its content to destination wav file.

    Read source raw file
    Write destination wav file with wave
    """

    source_file = filename
    dest_file = filename.split(".")[0] + "_test.wav"
    with open(filename, "rb") as raw_file:
        raw_data = raw_file.read()
    with wave.open(dest_file, "wb") as wav_file:
        wav_file.setparams((1, 2, 48000, 0, "NONE", "NONE"))
        wav_file.writeframes(raw_data)
    return dest_file


def generate_speech_from_text(text):
    """
    Generate wav audio file from input text.

    Get params from env variables
    Get audio content from input text with synthesize_audio()
    Write it to raw file
    Convert raw to wav with convert_raw_to_wav()
    Return result wav file
    """

    folder_id = os.getenv("FOLDER_ID")
    token = os.getenv("IAM_TOKEN")
    output = "speech.raw"

    audio_content = synthesize_audio(folder_id, token, text)
    with open(output, "wb") as f:
        f.write(audio_content)
    output_file = convert_raw_to_wav("speech.raw")
    return output_file


def prepare_wav(source_file="test_voice.wav"):
    """
    Set right parameters to input wav file.

    Read source wav file
    Write dest wav file with right params with wave
    Return dest file
    """

    dest_file = "new_test_voice.wav"

    with open(source_file, "rb") as src_file_wav:
        src_data = src_file_wav.read()

    with wave.open(dest_file, "wb") as dst_wav_file:
        dst_wav_file.setparams((1, 2, 48000, 0, "NONE", "NONE"))
        dst_wav_file.writeframes(src_data)

    return dest_file


def generate_text_from_speech(source_file):
    """
    Generate text from input wav audio file.

    Get params from env variables
    Update IAM token
    Convert source wav to wav with sox ???
    Set right params to converted wav with prepare_wav()
    Update IAM token ???
    Send POST request to Yandex STT service
    Return generated text from response
    """

    folder_id = os.getenv("FOLDER_ID")
    update_iam_token()
    token = os.getenv("IAM_TOKEN")
    voice_file = "text_from_speach_single.wav"

    # subprocess.call(['opusdec','--rate 48000', '--force-wav', source_file, voice_file])
    print(f"Converted {source_file} to {voice_file}")
    subprocess.call(["sox", source_file, voice_file])

    good_wav_file = prepare_wav(voice_file)
    print(
        f"Prepared {good_wav_file} from {voice_file} of size {os.path.getsize(good_wav_file)/1024}"
    )

    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

    with open(good_wav_file, "rb") as f:
        data = f.read()

    headers = {"Authorization": "Bearer " + token}

    params = {"format": "lpcm", "sampleRateHertz": 48000, "folderId": folder_id}

    # ???
    update_iam_token()

    resp = requests.post(url, params=params, data=data, headers=headers)

    if resp.status_code != 200:
        raise RuntimeError(
            "Invalid response received: code: %d, message: %s"
            % (resp.status_code, resp.text)
        )
    return resp.json()["result"]


def generate_text_from_long_speech(source_file):
    """
    Create list of texts generated from input ogg audio file with Yandex STT and return that list.

    Convert input ogg audio file to wav with 48K bit rate with opusdec ???
    Set right params to converted wav with prepare_wav() ???
    Print file size before and after prepare_wav() ???
    If size after is less than 1K:
        Generate text from this audio
        Assign result list to this text
    Else:
        Split big file in files <1K with check_wav_length ???
        For every small file:
            Generate text from audio with generate_text_from_speech()
            Append text to result list
    Return result list
    """

    list_of_texts = []
    subprocess.call(
        ["opusdec", "--rate", "48000", "--force-wav", source_file, "temp_wav_file.wav"]
    )
    # subprocess.call(['sox', source_file, 'temp_wav_file.wav'])
    print(f"Converted {source_file} to temp_wav_file.wav")

    file_size = os.path.getsize("temp_wav_file.wav") / 1024
    print(f"File temp_wav_file.wav first size {file_size}")

    # ??? Function prepare_wav returns file, should assign this value to some var
    prepare_wav("temp_wav_file.wav")
    file_size = os.path.getsize("temp_wav_file.wav") / 1024
    print(f"Preparing file temp_wav_file.wav, new size {file_size}")

    if file_size < 1024:
        print("File is small, generating text")
        list_of_texts = [generate_text_from_speech("temp_wav_file.wav")]
        print(f"Generated text of length {len(list_of_texts[0])}")
    else:
        print("File is large, splitting it then generating text")
        list_of_audio_files = check_wav_length.do_the_thing("temp_wav_file.wav")
        print(f"Splitted temp_wav_file.wav into {list_of_audio_files}")
        for file in list_of_audio_files:
            print(f"Generating text from {file}")
            list_of_texts.append(generate_text_from_speech(file))
            print(f"New text length is {len(list_of_texts[-1])}")
    return list_of_texts


def test_from_ogg_to_wav(source_file):
    """
    Compare sizes of result files converted from ogg to wav with opus and sox.

    Convert input ogg file to wav file with opusdec
    Convert from input ogg file to dest wav file with sox
    Print sizes of converted files
    Print size comparison
    """

    subprocess.call(
        [
            "opusdec",
            "--rate",
            "48000",
            "--force-wav",
            source_file,
            "convert_with_opusdec.wav",
        ]
    )
    subprocess.call(["sox", source_file, "convert_with_sox.wav"])

    file_size_opus = os.path.getsize("convert_with_opusdec.wav") / 1024
    file_size_sox = os.path.getsize("convert_with_sox.wav") / 1024
    print(f"Opusdec size {file_size_opus}")
    print(f"Sox size {file_size_sox}")
    if file_size_opus == file_size_sox:
        print("Sizes of opus and sox converted files - EQUAL")
    else:
        print("Sizes of opus and sox converted files - NOT EQUAL")


if __name__ == "__main__":
    # generate_speech_from_text('Hello world')
    for text in generate_text_from_long_speech("test_voice.ogg"):
        print(text)
    # test_from_ogg_to_wav('test_voice.ogg')
