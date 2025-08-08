from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Optional

import streamlit as st

from quizgen import (
    ContentAnalyzer,
    DocumentProcessor,
    QuizConfig,
    QuizFormatter,
    QuestionGenerator,
    TextPreprocessor,
)

st.set_page_config(page_title="Intelligent Quiz Generator", layout="wide")

st.title("Intelligent Quiz Generator")

with st.sidebar:
    st.header("Quiz Configuration")
    num_mcq = st.number_input("MCQs", min_value=0, max_value=50, value=5)
    num_tf = st.number_input("True/False", min_value=0, max_value=50, value=5)
    num_fill = st.number_input("Fill in the blank", min_value=0, max_value=50, value=5)
    num_short = st.number_input("Short answer", min_value=0, max_value=50, value=3)
    max_opts = st.number_input("Options per MCQ", min_value=2, max_value=6, value=4)
    output_format = st.selectbox("Output format", ["json", "text", "pdf"], index=0)
    seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42)
    include_answers = st.checkbox("Include answers in preview", value=True)

uploaded = st.file_uploader("Upload a document (PDF, DOCX, TXT, HTML)", type=["pdf", "docx", "txt", "html", "htm"]) 

if uploaded is not None:
    tmp_path = Path(".tmp_upload_" + uploaded.name)
    tmp_path.write_bytes(uploaded.getvalue())

    if st.button("Generate Quiz"):
        with st.spinner("Analyzing document and generating questions..."):
            config = QuizConfig(
                num_mcq=int(num_mcq),
                num_true_false=int(num_tf),
                num_fill_blank=int(num_fill),
                num_short_answer=int(num_short),
                include_answers=bool(include_answers),
                max_options_per_mcq=int(max_opts),
                output_format=output_format,
                random_seed=int(seed),
            )

            processor = DocumentProcessor()
            preprocessor = TextPreprocessor()
            analyzer = ContentAnalyzer(preprocessor)
            generator = QuestionGenerator(random_seed=int(seed))
            formatter = QuizFormatter()

            document = processor.extract_text(str(tmp_path))
            processed = preprocessor.process(document.text)
            concepts = analyzer.extract_concepts(processed)
            questions = generator.create_questions(concepts, config)

            st.success(f"Generated {len(questions)} questions.")

            # Preview
            for idx, q in enumerate(questions, start=1):
                with st.expander(f"Q{idx} [{q.type} | {q.difficulty}] {q.text}"):
                    if q.options:
                        for opt in q.options:
                            st.write(f"- {opt}")
                    if include_answers:
                        st.markdown(f"**Answer**: {q.correct_answer}")
                        if q.explanation:
                            st.caption(q.explanation)

            # Downloads
            col1, col2, col3 = st.columns(3)
            with col1:
                j = formatter.to_json(questions)
                st.download_button("Download JSON", data=j, file_name="quiz.json", mime="application/json")
            with col2:
                t = formatter.to_text(questions)
                st.download_button("Download Text", data=t, file_name="quiz.txt", mime="text/plain")
            with col3:
                pdf_path = Path("quiz.pdf")
                pdf_path = formatter.to_pdf(questions, pdf_path)
                st.download_button(
                    "Download PDF", data=pdf_path.read_bytes(), file_name=pdf_path.name, mime="application/pdf"
                )

    # Cleanup tmp
    try:
        tmp_path.unlink(missing_ok=True)
    except Exception:
        pass