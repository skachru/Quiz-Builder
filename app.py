"""Browser interface for the quiz generator. Run with streamlit run app.py."""

import json
import os

import streamlit as st
from openai import AuthenticationError, OpenAI, OpenAIError, RateLimitError
from pydantic import ValidationError

from quiz_generator import generate_quiz


st.set_page_config(page_title="Any-Topic Quiz", page_icon="📝")
st.title("Any-Topic Quiz")
st.write("Pick a topic, generate 10 questions, and test your knowledge.")

if not os.environ.get("OPENAI_API_KEY"):
    st.info("Add OPENAI_API_KEY to the .env file beside app.py, then restart the app.")

with st.form("generate"):
    topic = st.text_input("What would you like to learn about?", placeholder="e.g. Solar system")
    generate = st.form_submit_button("Generate quiz", type="primary")

if generate:
    if not topic.strip():
        st.warning("Enter a topic first.")
    elif not os.environ.get("OPENAI_API_KEY"):
        st.error("An OpenAI API key is required to generate a quiz.")
    else:
        try:
            with st.spinner("Creating your quiz…"):
                with OpenAI(timeout=90.0, max_retries=1) as client:
                    quiz = generate_quiz(topic, client)
            for key in list(st.session_state):
                if key.startswith("answer_"):
                    del st.session_state[key]
            st.session_state.quiz = quiz
            st.session_state.quiz_topic = topic.strip()
            st.session_state.submitted = False
            st.session_state.graded_answers = []
        except AuthenticationError:
            st.error("The API key was rejected. Check your .env file and restart the app.")
        except RateLimitError:
            st.error("The API limit was reached. Check your API quota or try again later.")
        except OpenAIError:
            st.error("Could not reach the quiz service. Please try again later.")
        except (ValidationError, ValueError):
            st.error("The service did not return a valid, complete quiz. Please try again.")

if "quiz" in st.session_state:
    quiz = st.session_state.quiz
    submitted = st.session_state.submitted
    st.subheader(f"Quiz: {st.session_state.quiz_topic}")
    with st.form("answers"):
        answers = []
        for i, question in enumerate(quiz.questions):
            options = question.options.model_dump()
            answer = st.radio(
                f"{i + 1}. {question.question}",
                options=list(options),
                format_func=lambda key, choices=options: f"{key}. {choices[key]}",
                index=list(options).index(st.session_state.graded_answers[i]) if submitted else None,
                key=f"answer_{i}",
                disabled=submitted,
            )
            answers.append(answer)
        check = st.form_submit_button("Check answers", disabled=submitted)

    if check:
        if any(answer is None for answer in answers):
            st.warning("Answer all 10 questions before checking your score.")
        else:
            st.session_state.graded_answers = answers
            st.session_state.submitted = True
            st.rerun()

    if submitted:
        score = sum(st.session_state.graded_answers[i] == q.correct_answer for i, q in enumerate(quiz.questions))
        st.success(f"Your score: {score} / 10")
        for i, question in enumerate(quiz.questions):
            chosen = st.session_state.graded_answers[i]
            result = "Correct" if chosen == question.correct_answer else "Incorrect"
            with st.expander(f"{i + 1}. {result} — {question.question}"):
                st.write(f"Your answer: {chosen}")
                st.write(f"Correct answer: {question.correct_answer}. {getattr(question.options, question.correct_answer)}")
                st.write(question.explanation)
        st.download_button(
            "Download quiz and answer key (JSON)",
            data=json.dumps([q.model_dump() for q in quiz.questions], indent=2),
            file_name="quiz.json",
            mime="application/json",
        )
        if st.button("Try this quiz again"):
            for i in range(10):
                del st.session_state[f"answer_{i}"]
            st.session_state.submitted = False
            st.rerun()
    st.caption("AI-generated answers can contain mistakes. Review before using in assessments.")
