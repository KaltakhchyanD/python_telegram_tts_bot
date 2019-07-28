import os
from pathlib import Path
import unittest
import wave


from src.check_wav_length import (
    _get_audio_file_duration,
    _get_size_in_kb,
    convert_from_ogg_to_wav,
    _find_non_empty_wav_files,
    _split_wav_by_silence,
    _create_and_return_new_file_name,
    _delete_old_files,
)


class TestGetAudioFileDuration(unittest.TestCase):
    def test_correct_file(self):
        """
        Test correct file
        """
        test_file = "tests/unit/test_files/speech_test.wav"
        result = _get_audio_file_duration(test_file)
        self.assertEqual(result, 4.525)

    def test_empty_audio_file(self):
        """
        Test empty audio file
        """
        test_file = "tests/unit/test_files/empty_file.wav"
        result = _get_audio_file_duration(test_file)
        self.assertEqual(result, 0)

    def test_not_audio_file(self):
        """
        Test not audio file
        """
        test_file = "tests/unit/test_files/not_audio_file.txt"
        with self.assertRaises(wave.Error):
            result = _get_audio_file_duration(test_file)

    def test_not_existing_file(self):
        """
        Test not existing file
        """
        test_file = "tests/unit/test_files/123.wav"
        with self.assertRaises(FileNotFoundError):
            result = _get_audio_file_duration(test_file)

    def test_not_string_filename(self):
        """
        Test not string file name
        """
        test_file = 123
        with self.assertRaises(OSError):
            result = _get_audio_file_duration(test_file)

    def test_no_filename(self):
        """
        Test not passing filename to func
        """
        with self.assertRaises(TypeError):
            result = _get_audio_file_duration()


class TestGetSizeInKB(unittest.TestCase):
    def test_correct_file(self):
        """
        Test correct file
        """
        test_file = "tests/unit/test_files/speech_test.wav"
        result = _get_size_in_kb(test_file)
        self.assertEqual(result, 424.261_718_75)

    def test_empty_audio_file(self):
        """
        Test empty audio file
        """
        test_file = "tests/unit/test_files/empty_file.wav"
        result = _get_size_in_kb(test_file)
        self.assertEqual(result, 0)

    def test_not_audio_file(self):
        """
        Test not audio file
        """
        test_file = "tests/unit/test_files/not_audio_file.txt"
        result = _get_size_in_kb(test_file)
        self.assertEqual(result, 62.884_765_625)

    def test_not_existing_file(self):
        """
        Test not existing file
        """
        test_file = "tests/unit/test_files/123.wav"
        with self.assertRaises(FileNotFoundError):
            result = _get_size_in_kb(test_file)

    def test_not_string_filename(self):
        """
        Test not string file name
        """
        test_file = 123
        with self.assertRaises(OSError):
            result = _get_size_in_kb(test_file)

    def test_no_filename(self):
        """
        Test not passing filename to func
        """
        with self.assertRaises(TypeError):
            result = _get_size_in_kb()


class TestConvertFromOggToWav(unittest.TestCase):
    def test_correct_file(self):
        """
        Test correct file
        """
        test_file = "tests/unit/test_files/audio_from_telegram.ogg"
        result = convert_from_ogg_to_wav(test_file)
        self.assertEqual(result, "temp_wav_file.wav")
        self.assertTrue(Path(result).exists())
        os.remove(result)

    def test_wav_instead_of_ogg(self):
        """
        Test convertion of wav file instead of ogg
        """
        test_file = "tests/unit/test_files/speech_test.wav"
        with self.assertRaises(ValueError):
            result = convert_from_ogg_to_wav(test_file)

    def test_not_existing_file(self):
        """
        Test not existing file
        """
        test_file = "tests/unit/test_files/123.ogg"
        with self.assertRaises(FileNotFoundError):
            result = convert_from_ogg_to_wav(test_file)

    def test_not_string_filename(self):
        """
        Test not string file name
        """
        test_file = 123
        with self.assertRaises(AttributeError):
            result = convert_from_ogg_to_wav(test_file)

    def test_no_filename(self):
        """
        Test not passing filename to func
        """
        with self.assertRaises(TypeError):
            result = convert_from_ogg_to_wav()


class TestFindNonEmptyWavFiles(unittest.TestCase):
    def test_normal_case(self):
        """
        Test normal case
        """
        path = "tests/unit/test_files"
        result = _find_non_empty_wav_files("speech_test", path)
        self.assertEqual(result, ["speech_test.wav"])

    def test_files_too_short_case(self):
        """
        Test name pattern that matches only files that are too short
        """
        path = "tests/unit/test_files"
        result = _find_non_empty_wav_files("small_file", path)
        self.assertEqual(result, [])

    def test_no_name_match_case(self):
        """
        Test name pattern that matches no files
        """
        path = "tests/unit/test_files"
        result = _find_non_empty_wav_files("other_name", path)
        self.assertEqual(result, [])

    def test_empty_dir(self):
        """
        Test empty dir
        """
        path = "tests/unit/test_files/temp_dir"
        os.mkdir(path)
        result = _find_non_empty_wav_files("speech_test", path)
        self.assertEqual(result, [])
        os.rmdir(path)

    def test_not_existing_dir(self):
        """
        Test not existing dir
        """
        path = "tests/unit/test_files/some_dir"
        with self.assertRaises(FileNotFoundError):
            result = _find_non_empty_wav_files("speech_test", path)

    def test_not_string_dir_path(self):
        """
        Test int instead of dir path
        """
        path = 123
        with self.assertRaises(TypeError):
            result = _find_non_empty_wav_files("speech_test", path)

    def test_no_filename(self):
        """
        Test not passing filename pattern to func
        """
        with self.assertRaises(TypeError):
            result = _find_non_empty_wav_files()


class TestSplitWavBySilence(unittest.TestCase):
    def setUp(self):
        """
        Save initial cwd
        """
        self.first = os.getcwd()
        os.chdir("tests/unit/test_files/split_test")
        try:
            os.remove(".DS_Store")
        except FileNotFoundError:
            pass

    def tearDown(self):
        """
        Change to initial cwd
        """
        os.chdir(self.first)

    def test_normal_case(self):
        """
        Test normal case
        """
        result = _split_wav_by_silence("text_from_speach_old.wav")
        self.assertEqual(result, "new_small_file")
        files_and_dirs_in_dir = os.listdir(path=os.getcwd())
        self.assertEqual(len(files_and_dirs_in_dir), 103)
        for name in files_and_dirs_in_dir:
            if name.startswith("new_small_file"):
                os.remove(name)

    def test_ogg_instead_of_wav(self):
        """
        Test ogg file instead of wav
        """
        with self.assertRaises(ValueError):
            result = _split_wav_by_silence("audio_from_telegram.ogg")

    def test_txt_instead_of_wav(self):
        """
        Test txt file instead of wav
        """
        with self.assertRaises(ValueError):
            result = _split_wav_by_silence("not_audio_file.txt")

    def test_not_existing_file(self):
        """
        Test not existing file
        """
        with self.assertRaises(FileNotFoundError):
            result = _split_wav_by_silence("123.wav")

    def test_int_instead_of_file(self):
        """
        Test int instead of filename
        """
        with self.assertRaises(AttributeError):
            result = _split_wav_by_silence(123)


class TestCreateAndReturnNewFileName(unittest.TestCase):
    def setUp(self):
        """
        Save initial cwd
        """
        self.first = os.getcwd()
        os.chdir("tests/unit/test_files/new_filename_test")
        try:
            os.remove(".DS_Store")
        except FileNotFoundError:
            pass

    def tearDown(self):
        """
        Change to initial cwd
        """
        os.chdir(self.first)

    def test_single_file(self):
        """
        Test new filename creation 1 time
        """
        filename_list = ["file_0.wav"]
        result = _create_and_return_new_file_name(filename_list)
        self.assertEqual(result, "file_1.wav")
        files_and_dirs_in_dir = os.listdir(path=os.getcwd())
        self.assertEqual(len(files_and_dirs_in_dir), 1)
        for name in files_and_dirs_in_dir:
            if name.startswith("file_"):
                os.remove(name)

    def test_multiple_files(self):
        """
        Test new filename creation 5 times
        """
        filename_list = ["file_0.wav"]
        for i in range(5):
            result = _create_and_return_new_file_name(filename_list)
            self.assertEqual(result, f"file_{i+1}.wav")
        files_and_dirs_in_dir = os.listdir(path=os.getcwd())
        self.assertEqual(len(files_and_dirs_in_dir), 5)
        for name in files_and_dirs_in_dir:
            if name.startswith("file_"):
                os.remove(name)

    def test_empty_filename_list(self):
        """
        Test empty filename list
        """
        filename_list = []
        with self.assertRaises(IndexError):
            result = _create_and_return_new_file_name(filename_list)

    def test_no_filename(self):
        """
        Test not passing filename list to func
        """
        with self.assertRaises(TypeError):
            result = _create_and_return_new_file_name()

    def test_int_instead_of_str_in_filename_list(self):
        """
        Test int instead of str in filename list
        """
        filename_list = [123]
        with self.assertRaises(AttributeError):
            result = _create_and_return_new_file_name(filename_list)

    def test_not_correct_filename_list(self):
        """
        Test fiilename without extension in filename list
        """
        filename_list = ["123"]
        with self.assertRaises(ValueError):
            result = _create_and_return_new_file_name(filename_list)


if __name__ == "__main__":
    unittest.main()