# Any-Topic MCQ Quiz Generator

A Python CLI that accepts a topic and returns a JSON array of exactly ten multiple-choice questions using OpenAI Structured Outputs and Pydantic.

## 1. Install

Use Python 3.10 or newer. From this checkout:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 2. Understand the schema

Read `quiz_generator.py`:

- `Options` requires four nonempty, distinct choices named A, B, C, D.
- `Question` requires question text, options, an answer key restricted to A-D, and an explanation.
- `Quiz` requires exactly ten distinct questions.

View the generated JSON Schema without credentials or a network call:

```bash
.venv/bin/python quiz_generator.py --schema
```

The API receives an object containing `questions` because Structured Outputs requires an object at the root. The CLI prints its inner array for your application to consume.

## 3. Configure API access securely

Set `OPENAI_API_KEY` through your execution environment's secure credential mechanism. Do not commit it, paste it into chat, or put it into source code. The CLI reads this variable automatically. An API account with access to the chosen model and available quota is required; requests can incur charges.

## 4. Generate a quiz

```bash
.venv/bin/python quiz_generator.py "Solar system" > quiz.json
```

You can select another Structured Outputs compatible model with `--model MODEL_NAME`. Errors go to stderr with a nonzero exit status; check the exit status before consuming the output file.

Each array item looks like:

```json
{
  "question": "Which planet is closest to the Sun?",
  "options": {"A": "Venus", "B": "Mercury", "C": "Earth", "D": "Mars"},
  "correct_answer": "B",
  "explanation": "Mercury has the smallest orbital distance from the Sun."
}
```

Pydantic validates structure, option uniqueness, count, and answer-key membership. It cannot prove factual correctness: generated questions and answers need review before use in assessments. A model refusal or invalid output is reported as an error rather than returned as a partial quiz.

## 5. Run offline tests

```bash
.venv/bin/python -m unittest -v
```

These tests check validation and the mocked API integration without making paid requests. Live API behavior requires a separate run with credentials.
