import os
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from quiz_generator import Quiz
from test_quiz_generator import quiz_data


class AppTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()

    def test_empty_topic(self):
        app = self.app()
        app.button[0].click().run()
        self.assertIn("Enter a topic", app.warning[0].value)
        self.assertFalse(app.exception)

    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_missing_key(self):
        app = self.app()
        app.text_input[0].set_value("Physics")
        app.button[0].click().run()
        self.assertIn("API key is required", app.error[0].value)
        self.assertFalse(app.exception)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "offline-test-key"})
    @patch("quiz_generator.generate_quiz")
    def test_generate_grade_and_retry(self, generate):
        generate.return_value = Quiz.model_validate(quiz_data())
        app = self.app()
        app.text_input[0].set_value("Physics")
        app.button[0].click().run()
        self.assertEqual(len(app.radio), 10)
        app.button[1].click().run()
        self.assertIn("Answer all 10", app.warning[0].value)
        self.assertEqual(len(app.success), 0)
        for radio in app.radio:
            radio.set_value("B")
        app.button[1].click().run()
        self.assertEqual(app.success[0].value, "Your score: 10 / 10")
        self.assertTrue(all(radio.disabled for radio in app.radio))
        app.button[-1].click().run()
        self.assertTrue(all(radio.value is None for radio in app.radio))
        self.assertEqual(len(app.success), 0)
        generate.assert_called_once()
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
