from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from quizgen import (
    AnswerGenerator,
    ContentAnalyzer,
    DocumentProcessor,
    QuizConfig,
    QuizFormatter,
    QuestionGenerator,
    TextPreprocessor,
)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Intelligent Quiz Generator")
    p.add_argument("--input", required=True, help="Path to input document (PDF/DOCX/TXT/HTML)")
    p.add_argument("--num-mcq", type=int, default=5)
    p.add_argument("--num-tf", type=int, default=5)
    p.add_argument("--num-fill", type=int, default=5)
    p.add_argument("--num-short", type=int, default=3)
    p.add_argument("--out", type=str, default="quiz.json")
    p.add_argument("--format", choices=["json", "text", "pdf"], default="json")
    p.add_argument("--seed", type=int, default=42)
    return p


def main() -> None:
    args = build_arg_parser().parse_args()

    config = QuizConfig(
        num_mcq=args.num_mcq,
        num_true_false=args.num_tf,
        num_fill_blank=args.num_fill,
        num_short_answer=args.num_short,
        output_format=args.format,
        random_seed=args.seed,
    )

    processor = DocumentProcessor()
    preprocessor = TextPreprocessor()
    analyzer = ContentAnalyzer(preprocessor)
    generator = QuestionGenerator(random_seed=args.seed)
    formatter = QuizFormatter()

    document = processor.extract_text(args.input)
    processed = preprocessor.process(document.text)
    concepts = analyzer.extract_concepts(processed)
    questions = generator.create_questions(concepts, config)

    out_path = Path(args.out)
    if args.format == "json":
        out_path.write_text(formatter.to_json(questions), encoding="utf-8")
    elif args.format == "text":
        out_path.write_text(formatter.to_text(questions), encoding="utf-8")
    else:
        formatter.to_pdf(questions, out_path)

    print(f"Saved quiz to: {out_path.resolve()}")


if __name__ == "__main__":
    main()