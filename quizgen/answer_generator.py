from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from nltk.corpus import wordnet as wn


class AnswerGenerator:
    def __init__(self, random_seed: int = 42) -> None:
        random.seed(random_seed)

    def generate_distractors_from_wordnet(self, term: str, max_distractors: int = 3) -> List[str]:
        term = term.replace(" ", "_")
        distractors: List[str] = []
        try:
            synsets = wn.synsets(term)
        except LookupError:
            synsets = []
        for syn in synsets:
            for lemma in syn.lemmas():
                candidate = lemma.name().replace("_", " ")
                if candidate.lower() != term.lower() and candidate not in distractors:
                    distractors.append(candidate)
                if len(distractors) >= max_distractors:
                    break
            if len(distractors) >= max_distractors:
                break
        return distractors

    def generate_numeric_distractors(self, correct: str, max_distractors: int = 3) -> List[str]:
        try:
            value = float(correct)
        except ValueError:
            return []
        # Simple perturbations
        offsets = [-1, +1, -10, +10, -0.5, +0.5]
        random.shuffle(offsets)
        distractors = []
        for off in offsets:
            candidate = value + off
            distractors.append(str(int(candidate)) if candidate.is_integer() else f"{candidate:.2f}")
            if len(distractors) >= max_distractors:
                break
        return distractors

    def pick_plausible_distractors(self, 
                                   correct_answer: str, 
                                   pool_terms: List[str], 
                                   named_entities: List[str],
                                   numerical_facts: List[str],
                                   max_options: int = 4) -> List[str]:
        distractors: List[str] = []
        if correct_answer.isdigit() or self._looks_numeric(correct_answer):
            distractors.extend(self.generate_numeric_distractors(correct_answer, max_options - 1))
        else:
            distractors.extend(self.generate_distractors_from_wordnet(correct_answer, max_options - 1))
            # Add entity-based distractors
            for ent in named_entities:
                if ent.lower() != correct_answer.lower() and ent not in distractors:
                    distractors.append(ent)
                if len(distractors) >= max_options - 1:
                    break
            # Add pool term distractors
            for term in pool_terms:
                if term.lower() != correct_answer.lower() and term not in distractors:
                    distractors.append(term)
                if len(distractors) >= max_options - 1:
                    break
        # Trim to desired length
        return distractors[: max_options - 1]

    def _looks_numeric(self, text: str) -> bool:
        try:
            float(text)
            return True
        except ValueError:
            return False