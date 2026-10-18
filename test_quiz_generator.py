import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from pydantic import ValidationError

from quiz_generator import Quiz, generate_quiz


def quiz_data():
    return {"questions": [
        {"question": f"Question {i}?", "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
         "correct_answer": "B", "explanation": "Two is correct."}
        for i in range(10)
    ]}


class QuizTests(unittest.TestCase):
    def test_valid_quiz_round_trip(self):
        quiz = Quiz.model_validate(quiz_data())
        self.assertEqual(Quiz.model_validate_json(quiz.model_dump_json()), quiz)

    def test_invalid_count(self):
        for count in (9, 11):
            data = quiz_data()
            data["questions"] = (data["questions"] * 2)[:count]
            with self.subTest(count=count), self.assertRaises(ValidationError):
                Quiz.model_validate(data)

    def test_invalid_answer_key(self):
        data = quiz_data()
        data["questions"][0]["correct_answer"] = "E"
        with self.assertRaises(ValidationError):
            Quiz.model_validate(data)

    def test_duplicate_options(self):
        data = quiz_data()
        data["questions"][0]["options"]["B"] = " one "
        with self.assertRaises(ValidationError):
            Quiz.model_validate(data)

    def test_duplicate_questions(self):
        data = quiz_data()
        data["questions"][1]["question"] = " question 0? "
        with self.assertRaises(ValidationError):
            Quiz.model_validate(data)

    def test_blank_question(self):
        data = quiz_data()
        data["questions"][0]["question"] = "   "
        with self.assertRaises(ValidationError):
            Quiz.model_validate(data)

    def test_generation_requests_schema(self):
        client = Mock()
        expected = Quiz.model_validate(quiz_data())
        client.responses.parse.return_value = SimpleNamespace(status="completed", output_parsed=expected)
        self.assertEqual(generate_quiz("Physics", client), expected)
        self.assertIs(client.responses.parse.call_args.kwargs["text_format"], Quiz)

    def test_refusal(self):
        client = Mock()
        client.responses.parse.return_value = SimpleNamespace(status="completed", output_parsed=None)
        with self.assertRaises(ValueError):
            generate_quiz("Physics", client)

    def test_blank_topic_does_not_call_api(self):
        client = Mock()
        with self.assertRaises(ValueError):
            generate_quiz("  ", client)
        client.responses.parse.assert_not_called()


if __name__ == "__main__":
    unittest.main()
