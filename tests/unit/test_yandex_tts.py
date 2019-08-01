import os
import unittest

from src.yandex_tts import _update_iam_token


class TestUpdateIamToken(unittest.TestCase):
    def test_normal_case(self):
        """
        Test normal case 
        """
        temp_env_value = "Notarealtoken"
        os.environ["IAM_TOKEN"] = temp_env_value
        _update_iam_token()
        self.assertTrue(os.getenv("IAM_TOKEN")!= temp_env_value)