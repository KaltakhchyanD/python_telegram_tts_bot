"""
This module contains provides ability to perform TTS and STT with Yandex TTS and STT services.

It contains these functions:
generate_speech_from_text() - returns wav audio synthesized from input text
generate_text_from_speech() - returns text generated from input ogg audio
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
    Get IAM token with requests
    Update IAM token env var
    """

    OauthToken = str(os.getenv("OauthToken"))
    OauthToken_string = '{"yandexPassportOauthToken": "' + OauthToken + '"}'

    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    data = {"yandexPassportOauthToken": OauthToken}
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, data=json.dumps(data))

    if resp.status_code != 200:
        raise RuntimeError(
            "Invalid response received: code: %d, message: %s"
            % (resp.status_code, resp.text)
        )
    new_iam_token = resp.json()["iamToken"]
    os.environ["IAM_TOKEN"] = new_iam_token


def synthesize_audio_from_text(folder_id, iam_token, text):
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


def generate_speech_from_text(text):
    """
    Generate wav audio file from input text.

    Get params from env variables
    Get audio content from input text with synthesize_audio_from_text()
    Write it to wav file
    Return result wav file
    """

    folder_id = os.getenv("FOLDER_ID")
    token = os.getenv("IAM_TOKEN")
    output_wav_file = "tts_output.wav"

    audio_content = synthesize_audio_from_text(folder_id, token, text)

    with wave.open(output_wav_file, "wb") as wav_file:
        wav_file.setparams((1, 2, 48000, 0, "NONE", "NONE"))
        wav_file.writeframes(audio_content)

    return output_wav_file


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


def synthesize_text_from_audio(source_file):
    """
    Synthesize text from input wav audio file.

    Update IAM token
    Get params from env variables
    Send POST request to Yandex STT service
    Return generated text from response
    """

    update_iam_token()
    folder_id = os.getenv("FOLDER_ID")
    token = os.getenv("IAM_TOKEN")

    with open(source_file, "rb") as f:
        data = f.read()

    url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
    headers = {"Authorization": "Bearer " + token}
    params = {"format": "lpcm", "sampleRateHertz": 48000, "folderId": folder_id}
    resp = requests.post(url, params=params, data=data, headers=headers)

    if resp.status_code != 200:
        raise RuntimeError(
            "Invalid response received: code: %d, message: %s"
            % (resp.status_code, resp.text)
        )
    return resp.json()["result"]


def generate_text_from_speech(source_file):
    """
    Create list of texts generated from input ogg audio file with Yandex STT and return that list.

    Convert input ogg audio file to wav with check_wav_length.convert_from_ogg_to_wav()
    Create list of files smaller than 1K from converted wav file
    For every file in list:
        Generate text from audio with synthesize_text_from_audio()
        Add it to result text
    Return result text
    """

    list_of_texts = []
    result_text = ""
    wav_from_ogg = check_wav_length.convert_from_ogg_to_wav(source_file)
    print("OGG TO WAV - SUCCESS")
    list_of_audio_files = check_wav_length.split_into_files_less_than_1k(wav_from_ogg)
    print("BIG TO SMALL - SUCCESS")
    for file in list_of_audio_files:
        result_text += synthesize_text_from_audio(file)
    print("VOICE TO TEXT - SUCCESS")
    return result_text


def test_from_ogg_to_wav(source_file):
    """
    Compare sizes of result files converted from ogg to wav with opus and sox.

    Convert input ogg file to wav file with opusdec
    Convert from input ogg file to dest wav file with sox
    Print sizes of converted files
    Print size comparison
    """
    from pydub import AudioSegment

    from_ogg_pydub = AudioSegment.from_ogg(source_file)
    from_ogg_pydub.export("convert_with_pydub.wav", bitrate="48k", format="wav")

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
    file_size_pydub = os.path.getsize("convert_with_pydub.wav") / 1024

    print(f"Opusdec size {file_size_opus}")
    print(f"Sox size {file_size_sox}")
    print(f"Pydub size {file_size_pydub}")
    if file_size_opus == file_size_sox:
        print("Sizes of opus and sox converted files - EQUAL")
    else:
        print("Sizes of opus and sox converted files - NOT EQUAL")


if __name__ == "__main__":
    # test_one = generate_text_from_speech("test_voice.ogg")
    # print(test_one)
    test_from_ogg_to_wav("test_voice.ogg")
