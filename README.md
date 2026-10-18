# Any-Topic MCQ Quiz Generator

A browser UI and Python CLI that accept a topic and return exactly ten multiple-choice questions using OpenAI Structured Outputs and Pydantic.

## Start the browser UI on Windows

From your quiz-builder directory, with your virtual environment activated:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Streamlit opens your browser and prints the local address in your terminal. Enter a topic, click **Generate quiz**, select all ten answers, then click **Check answers**. You can review explanations, download the quiz and answer key as JSON, or retry without another API request. Generating a new quiz makes a new API request.

Keep your API key in a file named `.env` beside `app.py`:

```dotenv
OPENAI_API_KEY=your_actual_api_key
```

Both the UI and CLI load this file automatically. Existing process environment variables take precedence. Restart Streamlit after changing the key. Never commit `.env`; it is excluded by `.gitignore`.

This UI is intended for personal local use. It has no user authentication; do not expose your API-backed instance publicly without adding access controls. Quiz contents stay in the current Streamlit session unless downloaded.

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

Set `OPENAI_API_KEY` in the local `.env` file as described above or through your execution environment's secure credential mechanism. Do not commit it, paste it into chat, or put it into source code. An API account with access to the chosen model and available quota is required; requests can incur charges.

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
