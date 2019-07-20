"""
check_wav_length.py
-------------------
This module provides ability to split wav audio file into several files of size <1K.

It contains these functions to export:

* convert_from_ogg_to_wav() - creates new wav file from input ogg, returns it
* split_into_files_less_than_1k() - takes source wav file, returns list of smaller wav files of size <1K.
"""

import logging
import os
import wave
import subprocess

from pydub import AudioSegment

# logger = logging.getLogger()


def _get_audio_file_duration(filename):
    """Get duration by divising number of frames to framerate with wave."""
    # this is hack i think, should revisit later
    duration = 0
    if os.path.getsize(filename):
        # try:
        with wave.open(filename) as wav_f:
            frames = wav_f.getnframes()
            rate = wav_f.getframerate()
            duration = frames / float(rate)
        # except wave.Error as e:
        #    logger.exception(f"Wave - error during reading {filename} ")
        # raise
    return duration


def _get_size_in_kb(filename):
    """Get size of file in KB."""
    return os.path.getsize(filename) / 1024


def convert_from_ogg_to_wav(ogg_audio_file):
    """Take ogg audio file and convert it to wav audio file."""
    wav_from_ogg = "temp_wav_file.wav"
    # subprocess.call(
    #    ["opusdec", "--rate", "48000", "--force-wav", ogg_audio_file, wav_from_ogg]
    # )

    from_ogg_pydub = AudioSegment.from_ogg(ogg_audio_file)
    from_ogg_pydub.export(wav_from_ogg, bitrate="48k", format="wav")

    # subprocess.call(['sox', ogg_audio_file, wav_from_ogg])
    print(f"Converted {ogg_audio_file} to {wav_from_ogg}")
    return wav_from_ogg


def _find_non_empty_files(name_pattern):
    """
    Return list of non-empty wav files in dir

    Get files if current dir
    Get all wav files with certain name with duration>0.5s ??? names of result of splitting by silence
    Return list of not empty wav files
    """

    files_and_dirs_in_cwd = os.listdir(path=os.getcwd())
    non_empty_small_wav_files = [
        i
        for i in sorted(files_and_dirs_in_cwd)
        if ".wav" in i and _get_audio_file_duration(i) >= 0.5 and name_pattern in i
    ]

    # print(f"NOT EMPTY FILES {non_empty_small_wav_files}")
    return non_empty_small_wav_files


def _split_wav_by_silence(source_wav):
    """
    Split wav audio on silence(silence is 0.1 sec of 2% of max volume(of sample?)).
    Return list of non-empty small files
    """

    subprocess.call(
        [
            "sox",
            source_wav,
            "new_small_file.wav",
            "silence",
            "0",
            "1",
            "0.1",
            "2%",
            ":",
            "newfile",
            ":",
            "restart",
        ]
    )
    non_empty_small_wav_files = _find_non_empty_files("new_small_file")
    return non_empty_small_wav_files


def _create_and_return_new_file_name(result_audio_files):
    """
    Create and append new filename to list of names by adding _1 to the last filename.
    Return new filename
    """

    last_name = result_audio_files[-1]
    name_without_extention = last_name.split(".")[0]
    new_index = int(name_without_extention.split("_")[-1]) + 1
    new_name = "_".join(name_without_extention.split("_")[:-1]) + str(new_index)

    with open(new_name, "w") as f:
        pass
    result_audio_files.append(new_name)
    return new_name


def _delete_old_files():
    """Delete wav files that was created by split by silence and temp files. ???"""
    files_and_dirs_in_cwd = os.listdir(path=os.getcwd())
    non_empty_small_wav_files = [
        i for i in sorted(files_and_dirs_in_cwd) if ".wav" in i
    ]
    print("Cleaning up")
    print(f"{len(non_empty_small_wav_files)} files to delete")
    for filename in non_empty_small_wav_files:
        if "new_small_file" in filename or "generated_audio_file" in filename:
            # print(f"Deleting file {filename}")
            os.remove(filename)


def _add_first_audio_file_to_second(first_file, second_file):
    """
    Read 2 wav audio files, add audio data of first to second, write to second file
    """
    with open(second_file, "rb") as second_file_wav:
        second_file_data = second_file_wav.read()

    with open(first_file, "rb") as first_file_wav:
        first_file_data = first_file_wav.read()

    with wave.open(second_file, "wb") as dst_wav_file:
        dst_wav_file.setparams((1, 2, 48000, 0, "NONE", "NONE"))
        dst_wav_file.writeframes(second_file_data + first_file_data)


def split_into_files_less_than_1k(source_wav):
    """
    Split source wav file into files of size <1K.

    Clean up dir - delete old files
    Split input wav file by silence
    Add up small files into files of size <1K
    Return list of result filenames(that are <1K)
    """
    # 1
    _delete_old_files()

    # 2/3
    if _get_size_in_kb(source_wav) < 1024:
        result_audio_files = [source_wav]
    else:
        print("Splitting to small files")
        non_empty_small_wav_files = _split_wav_by_silence(source_wav)

        # create first empty file to append audio content to
        result_audio_files = ["generated_audio_file_0.wav"]
        with open(result_audio_files[0], "wb") as _:
            pass

        # 4
        # itterate over small files
        # add small file to last result audio file while its size is less than 1KB
        # then create new result audio file
        # and add small file to it
        for next_small_file in non_empty_small_wav_files:
            current_result_audio_file = result_audio_files[-1]

            small_file_size = _get_size_in_kb(next_small_file)
            last_big_file_size = _get_size_in_kb(current_result_audio_file)

            if 1024 < last_big_file_size + small_file_size:
                current_result_audio_file = _create_and_return_new_file_name(
                    result_audio_files
                )
            _add_first_audio_file_to_second(next_small_file, current_result_audio_file)
        print(result_audio_files)
    return result_audio_files


if __name__ == "__main__":
    split_into_files_less_than_1k(source_wav="text_from_speach.wav")
