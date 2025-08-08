from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from .question_generator import Question


class QuizFormatter:
    def __init__(self) -> None:
        pass

    def to_json(self, questions: List[Question]) -> str:
        payload = [asdict(q) for q in questions]
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def to_text(self, questions: List[Question]) -> str:
        lines = []
        for idx, q in enumerate(questions, start=1):
            lines.append(f"Q{idx} [{q.type} | {q.difficulty}]: {q.text}")
            if q.options:
                for opt_idx, opt in enumerate(q.options, start=1):
                    lines.append(f"  {chr(96+opt_idx)}) {opt}")
            lines.append(f"Answer: {q.correct_answer}")
            if q.explanation:
                lines.append(f"Explanation: {q.explanation}")
            lines.append("")
        return "\n".join(lines)

    def to_pdf(self, questions: List[Question], out_path: Path) -> Path:
        try:
            from reportlab.lib.pagesizes import LETTER
            from reportlab.pdfgen import canvas
        except Exception as exc:
            # Fallback to text if reportlab unavailable
            out_path = out_path.with_suffix('.txt')
            out_path.write_text(self.to_text(questions), encoding='utf-8')
            return out_path

        c = canvas.Canvas(str(out_path), pagesize=LETTER)
        width, height = LETTER
        x_margin, y_margin = 40, 40
        x, y = x_margin, height - y_margin
        line_height = 14

        def draw_line(text: str) -> None:
            nonlocal y
            if y < y_margin:
                c.showPage()
                y = height - y_margin
            c.drawString(x, y, text[:95])
            y -= line_height

        for idx, q in enumerate(questions, start=1):
            draw_line(f"Q{idx} [{q.type} | {q.difficulty}]: {q.text}")
            if q.options:
                for opt_idx, opt in enumerate(q.options, start=1):
                    draw_line(f"  {chr(96+opt_idx)}) {opt}")
            draw_line(f"Answer: {q.correct_answer}")
            if q.explanation:
                draw_line(f"Explanation: {q.explanation}")
            draw_line("")
        c.save()
        return out_path