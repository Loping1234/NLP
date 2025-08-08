# Intelligent Quiz Generator (MVP)

An NLP system that generates quizzes (MCQ, True/False, Fill-in-the-blank, Short Answer) from uploaded documents (PDF, DOCX, TXT, HTML).

## Quickstart

1. Create and activate a virtual environment (recommended)

```bash
python3 -m venv .venv && source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
python - <<'PY'
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
PY
```

Optional: Install spaCy + English model for stronger NER and parsing

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

3. Run the CLI

```bash
python app.py --input sample.txt --num-mcq 5 --num-tf 3 --num-fill 3 --num-short 2 --out quiz.json
```

4. Launch the web UI (Streamlit)

```bash
streamlit run web_interface.py
```

## Features

- Document processing: PDF, DOCX, TXT, HTML
- Text analysis: tokenization, TF-IDF key terms, simple definition/number extraction, optional NER
- Question generation: MCQ, True/False, Fill-in-the-blank, Short answer
- Difficulty assessment: heuristic (frequency, sentence complexity)
- Answer key generation: correct answer + plausible distractors
- Output: JSON, printable text, PDF (ReportLab)

## Structure

```
quizgen/
  __init__.py
  config.py
  document_processor.py
  nlp_utils.py
  text_analyzer.py
  question_generator.py
  difficulty_assessor.py
  answer_generator.py
  quiz_formatter.py
app.py
web_interface.py
requirements.txt
README.md
tests/
  test_analyzer.py
  test_question_generator.py
```

## Notes

- This is a baseline implementation optimized for clarity and extensibility. You can incrementally replace heuristics with advanced models (BERT/GPT, QA, summarization) as needed.
- If `spacy` or its model is unavailable, the system gracefully degrades to NLTK-only features.
- For PDF generation, we use ReportLab; the app will fallback to text/JSON if PDF generation fails.