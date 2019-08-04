import os
import unittest
from unittest.mock import patch

import requests

from src.yandex_tts import (
    _update_iam_token,
    CURRENT_LANG,
    change_current_lang_and_return,
    _synthesize_audio_content_from_text,
    generate_audio_file_from_text,
    _synthesize_text_from_audio_file,
    generate_text_from_speech,
)

from src.check_wav_length import _delete_old_files


class TestUpdateIamToken(unittest.TestCase):
    def test_normal_case(self):
        """
        Test normal case 
        """
        temp_env_value = "Notarealtoken"
        os.environ["IAM_TOKEN"] = temp_env_value
        _update_iam_token()
        self.assertTrue(os.getenv("IAM_TOKEN") != temp_env_value)

    def test_requests_404(self):
        """
        Test mocked resp returns 404
        """
        with patch("src.yandex_tts.requests") as mock_requests:
            mock_requests.status_code = 404
            with self.assertRaises(RuntimeError):
                _update_iam_token()

    @patch.object(requests, "post", side_effect=requests.exceptions.Timeout)
    def test_requests_timeout(self, mock_requests):
        """
        Test mocked requests post raises timeout
        """
        with self.assertRaises(requests.exceptions.Timeout):
            _update_iam_token()


class TestChangeCurrentLang(unittest.TestCase):
    def test_normal_case(self):
        """
        Test normal case 
        """
        new_lang = "Not the same"
        self.assertEqual(change_current_lang_and_return(new_lang), new_lang)
        change_current_lang_and_return("en-US")


class TestSynthesizeAudioContentFromText(unittest.TestCase):
    def setUp(self):
        self.text_to_genarate = "One two three fore uno dos tres quatro"
        self.folder_id = os.getenv("FOLDER_ID")
        self.token = os.getenv("IAM_TOKEN")

    def test_normal_case(self):
        """
        Test normal case 
        """
        result_audio = _synthesize_audio_content_from_text(
            self.folder_id, self.token, self.text_to_genarate
        )
        self.assertEqual(len(result_audio), 318240)

    def test_requests_404(self):
        """
        Test mocked resp returns 404
        """
        with patch("src.yandex_tts.requests") as mock_requests:
            mock_requests.status_code = 404
            with self.assertRaises(RuntimeError):
                _synthesize_audio_content_from_text(
                    self.folder_id, self.token, self.text_to_genarate
                )

    @patch.object(requests, "post", side_effect=requests.exceptions.Timeout)
    def test_requests_timeout(self, mock_requests):
        """
        Test mocked requests post raises timeout
        """
        with self.assertRaises(requests.exceptions.Timeout):
            _synthesize_audio_content_from_text(
                self.folder_id, self.token, self.text_to_genarate
            )

    def test_without_folder_id(self):
        """
        Test without folder id
        """
        with self.assertRaises(TypeError):
            result_audio = _synthesize_audio_content_from_text(
                iam_token=self.token, text=self.text_to_genarate
            )

    def test_without_token(self):
        """
        Test without token
        """
        with self.assertRaises(TypeError):
            result_audio = _synthesize_audio_content_from_text(
                folder_id=self.folder_id, text=self.text_to_genarate
            )

    def test_without_text(self):
        """
        Test without text
        """
        with self.assertRaises(TypeError):
            result_audio = _synthesize_audio_content_from_text(
                folder_id=self.folder_id, iam_token=self.token
            )

    def test_empty_text(self):
        """
        Test with empty text
        """
        with self.assertRaises(RuntimeError):
            result_audio = _synthesize_audio_content_from_text(
                folder_id=self.folder_id, iam_token=self.token, text=""
            )


class TestGenerateAudioFileFromText(unittest.TestCase):
    def setUp(self):
        self.text_to_genarate = "One two three fore uno dos tres quatro"
        self.first = os.getcwd()
        os.chdir("tests/unit/test_files")

    def tearDown(self):
        """
        Change to initial cwd
        """
        os.chdir(self.first)

    def test_normal_case(self):
        """
        Test normal case 
        """
        files_before = len(os.listdir())
        generate_audio_file_from_text(self.text_to_genarate)
        files_after = len(os.listdir())
        self.assertEqual(files_after, files_before + 1)
        self.assertTrue("tts_output.wav" in os.listdir())
        os.remove("tts_output.wav")

    def test_requests_404(self):
        """
        Test mocked resp returns 404
        """
        with patch("src.yandex_tts.requests") as mock_requests:
            mock_requests.status_code = 404
            with self.assertRaises(RuntimeError):
                generate_audio_file_from_text(self.text_to_genarate)

    @patch.object(requests, "post", side_effect=requests.exceptions.Timeout)
    def test_requests_timeout(self, mock_requests):
        """
        Test mocked requests post raises timeout
        """
        with self.assertRaises(requests.exceptions.Timeout):
            generate_audio_file_from_text(self.text_to_genarate)

    def test_without_text(self):
        """
        Test without text
        """
        with self.assertRaises(TypeError):
            generate_audio_file_from_text()

    def test_empty_text(self):
        """
        Test without text
        """
        with self.assertRaises(RuntimeError):
            generate_audio_file_from_text("")


class TestSynthesizeTextFromAudioFile(unittest.TestCase):
    def setUp(self):
        self.audio_file = "tests/unit/test_files/stt_audio.wav"
        self.folder_id = os.getenv("FOLDER_ID")
        self.token = os.getenv("IAM_TOKEN")

    def test_normal_case(self):
        """
        Test normal case 
        """
        result_text = _synthesize_text_from_audio_file(
            self.folder_id, self.token, self.audio_file
        )
        self.assertTrue(
            result_text
            in ["One two three fore uno dos tres quatro", "1234 in a dos truskawkowa"]
        )

    def test_requests_404(self):
        """
        Test mocked resp returns 404
        """
        with patch("src.yandex_tts.requests") as mock_requests:
            mock_requests.status_code = 404
            with self.assertRaises(RuntimeError):
                _synthesize_text_from_audio_file(
                    self.folder_id, self.token, self.audio_file
                )

    @patch.object(requests, "post", side_effect=requests.exceptions.Timeout)
    def test_requests_timeout(self, mock_requests):
        """
        Test mocked requests post raises timeout
        """
        with self.assertRaises(requests.exceptions.Timeout):
            _synthesize_text_from_audio_file(
                self.folder_id, self.token, self.audio_file
            )

    def test_without_folder_id(self):
        """
        Test without folder id
        """
        with self.assertRaises(TypeError):
            result_audio = _synthesize_text_from_audio_file(
                iam_token=self.token, source_file=self.audio_file
            )

    def test_without_token(self):
        """
        Test without token
        """
        with self.assertRaises(TypeError):
            result_audio = _synthesize_text_from_audio_file(
                folder_id=self.folder_id, source_file=self.audio_file
            )

    def test_without_text(self):
        """
        Test without source_file
        """
        with self.assertRaises(TypeError):
            result_audio = _synthesize_text_from_audio_file(
                folder_id=self.folder_id, iam_token=self.token
            )

    def test_empty_text(self):
        """
        Test with empty source_file
        """
        with self.assertRaises(FileNotFoundError):
            result_audio = _synthesize_text_from_audio_file(
                folder_id=self.folder_id, iam_token=self.token, source_file=""
            )


class TestGenerateTextFromSpeech(unittest.TestCase):
    def setUp(self):
        self.audio_file = "tests/unit/test_files/stt_audio.ogg"
        change_current_lang_and_return("ru-RU")

    def tearDown(self):
        _delete_old_files()
        change_current_lang_and_return("en-US")

    def test_normal_case(self):
        """
        Test normal case 
        """
        self.assertEqual(
            generate_text_from_speech(self.audio_file),
            "24(678)910-11-12 13 14 15 16 17 1819 20",
        )

    def test_requests_404(self):
        """
        Test mocked resp returns 404
        """
        with patch("src.yandex_tts.requests") as mock_requests:
            mock_requests.status_code = 404
            with self.assertRaises(RuntimeError):
                generate_text_from_speech(self.audio_file)

    @patch.object(requests, "post", side_effect=requests.exceptions.Timeout)
    def test_requests_timeout(self, mock_requests):
        """
        Test mocked requests post raises timeout
        """
        with self.assertRaises(requests.exceptions.Timeout):
            generate_text_from_speech(self.audio_file)

    def test_without_text(self):
        """
        Test without text
        """
        with self.assertRaises(TypeError):
            generate_text_from_speech()

    def test_empty_text(self):
        """
        Test without text
        """
        with self.assertRaises(ValueError):
            generate_text_from_speech("")


if __name__ == "__main__":
    unittest.main()
