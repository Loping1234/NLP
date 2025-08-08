from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


class DifficultyAssessor:
    def __init__(self) -> None:
        pass

    def assess(self, *, importance_score: float, sentence_length: int) -> str:
        # Heuristic: low frequency (low importance) + long sentence => harder
        score = (1.0 - importance_score) * 0.6 + (min(sentence_length, 40) / 40.0) * 0.4
        if score < 0.33:
            return "easy"
        if score < 0.66:
            return "medium"
        return "hard"