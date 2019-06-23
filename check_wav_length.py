"""
This module provides ability to split wav audio file into several files of size <1K.

It contains these functions to export:
split_into_files_less_than_1k() - takes source wav file, returns list of smaller wav files of size <1K.
"""


import os
import wave
import subprocess

from pydub import AudioSegment


def get_audio_file_duration(filename):
    """Get duration by divising number of frames to framerate with wave."""
    # this is hack i think, should revisit later
    duration = 0
    if os.path.getsize(filename):
        with wave.open(filename) as wav_f:
            frames = wav_f.getnframes()
            rate = wav_f.getframerate()
            duration = frames / float(rate)
    return duration


def get_size_in_kb(filename):
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


def split_wav_by_silence(source_wav):
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
    not_empty_wav_files = find_not_empty_files("new_small_file")
    return not_empty_wav_files


def find_not_empty_files(name_pattern):
    """
    Return list of non-empty wav files in dir

    Get files if current dir
    Get all wav files with certain name with duration>0.5s ??? names of result of splitting by silence
    Return list of not empty wav files
    """

    files_and_dirs_in_cwd = os.listdir(path=os.getcwd())
    not_empty_wav_files = [
        i
        for i in sorted(files_and_dirs_in_cwd)
        if ".wav" in i and get_audio_file_duration(i) >= 0.5 and name_pattern in i
    ]

    print(f"NOT EMPTY FILES {not_empty_wav_files}")
    return not_empty_wav_files


def create_new_file_name(list_of_names):
    """
    Create and append new filename to list of names by adding _1 to the last filename.
    Return new filename
    """

    last_name = list_of_names[-1]
    new_name = last_name.split(".")[0] + "_1" + ".wav"
    with open(new_name, "w") as f:
        pass
    list_of_names.append(new_name)
    return new_name


def delete_old_files():
    """Delete wav files that was created by split by silence and temp files. ???"""
    files_and_dirs_in_cwd = os.listdir(path=os.getcwd())
    not_empty_wav_files = [i for i in sorted(files_and_dirs_in_cwd) if ".wav" in i]
    print("Cleaning up")
    print(f"{len(not_empty_wav_files)} files to delete")
    for filename in not_empty_wav_files:
        if "new_small_file" in filename or "generated_audio_file" in filename:
            # print(f"Deleting file {filename}")
            os.remove(filename)


def split_into_files_less_than_1k(source_wav):
    """
    Split source wav file into files of size <1K.

    Clean up dir - delete old files
    Split input wav file at silence
    Add up small files into files of size <1K
    Return list of filenames(that are <1K)
    """
    # 1
    delete_old_files()
    # 2/3
    if get_size_in_kb(source_wav) < 1024:
        list_of_names = [source_wav]
    else:
        print("Splitting to small files")
        not_empty_wav_files = split_wav_by_silence(source_wav)
        list_of_names = ["generated_audio_file.wav"]
        with open(list_of_names[0], "wb") as dst_wav_file:
            pass
        print(f"Start size {get_size_in_kb(list_of_names[-1])}")

        # 4
        for next_small_file in not_empty_wav_files:
            small_file_size = os.path.getsize(next_small_file) / 1024

            print(f"File - {next_small_file}, size - {small_file_size} kb")
            current_big_file = list_of_names[-1]
            current_size = get_size_in_kb(current_big_file)

            if current_size + small_file_size < 1024:
                pass
            else:
                print("     ------- LONG FILE")
                current_big_file = create_new_file_name(list_of_names)

            with open(current_big_file, "rb") as src_file_wav:
                src_data = src_file_wav.read()
            with open(next_small_file, "rb") as file_wav:
                file_data = file_wav.read()
            with wave.open(current_big_file, "wb") as dst_wav_file:
                dst_wav_file.setparams((1, 2, 48000, 0, "NONE", "NONE"))
                dst_wav_file.writeframes(src_data + file_data)

            print(f"New size {get_size_in_kb(current_big_file)}")

        print(list_of_names)
    return list_of_names


if __name__ == "__main__":
    split_into_files_less_than_1k(source_wav="text_from_speach.wav")
