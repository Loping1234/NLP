from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from .answer_generator import AnswerGenerator
from .difficulty_assessor import DifficultyAssessor
from .text_analyzer import Concept


@dataclass
class Question:
    type: str  # mcq|true_false|fill_blank|short_answer
    text: str
    options: Optional[List[str]]
    correct_answer: str
    explanation: Optional[str]
    difficulty: str
    source_reference: Optional[str]


class QuestionGenerator:
    def __init__(self, random_seed: int = 42) -> None:
        random.seed(random_seed)
        self.difficulty = DifficultyAssessor()
        self.answers = AnswerGenerator(random_seed=random_seed)

    def create_questions(self, concepts: List[Concept], config) -> List[Question]:
        questions: List[Question] = []
        pool_terms = [c.term for c in concepts]

        # MCQ
        for concept in concepts:
            if len(questions) >= config.num_mcq:
                break
            q = self._make_mcq(concept, pool_terms, config.max_options_per_mcq)
            if q:
                questions.append(q)

        # True/False
        tf_count = 0
        for concept in concepts:
            if tf_count >= config.num_true_false:
                break
            q = self._make_true_false(concept)
            if q:
                questions.append(q)
                tf_count += 1

        # Fill in the blank
        fb_count = 0
        for concept in concepts:
            if fb_count >= config.num_fill_blank:
                break
            q = self._make_fill_blank(concept)
            if q:
                questions.append(q)
                fb_count += 1

        # Short answer
        sa_count = 0
        for concept in concepts:
            if sa_count >= config.num_short_answer:
                break
            q = self._make_short_answer(concept)
            if q:
                questions.append(q)
                sa_count += 1

        return questions

    def _make_mcq(self, concept: Concept, pool_terms: List[str], max_options: int) -> Optional[Question]:
        sentence = (concept.definition_candidates or concept.supporting_sentences or [""])[0]
        if not sentence:
            return None
        # Try definition-based question
        prompt = f"What is '{concept.term}'?"
        correct = self._extract_definition_or_term(concept)
        if not correct:
            correct = concept.term

        distractors = self.answers.pick_plausible_distractors(
            correct, pool_terms, concept.named_entities, concept.numerical_facts, max_options
        )
        options = [correct] + distractors
        random.shuffle(options)

        difficulty = self.difficulty.assess(
            importance_score=concept.importance_score, sentence_length=len(sentence.split())
        )
        return Question(
            type="mcq",
            text=prompt,
            options=options,
            correct_answer=correct,
            explanation=sentence,
            difficulty=difficulty,
            source_reference=sentence,
        )

    def _make_true_false(self, concept: Concept) -> Optional[Question]:
        sentence = (concept.supporting_sentences or [""])[0]
        if not sentence:
            return None
        # 50% chance to flip a factual element if numeric is present
        statement = sentence
        correct_answer = "True"
        if concept.numerical_facts:
            # Simple perturbation: change first number by +1
            num = concept.numerical_facts[0]
            if num in statement:
                try:
                    new_val = str(int(float(num)) + 1)
                    statement = statement.replace(num, new_val, 1)
                    correct_answer = "False"
                except ValueError:
                    pass
        difficulty = self.difficulty.assess(
            importance_score=concept.importance_score, sentence_length=len(sentence.split())
        )
        return Question(
            type="true_false",
            text=statement,
            options=["True", "False"],
            correct_answer=correct_answer,
            explanation=sentence,
            difficulty=difficulty,
            source_reference=sentence,
        )

    def _make_fill_blank(self, concept: Concept) -> Optional[Question]:
        sentence = (concept.supporting_sentences or [""])[0]
        if not sentence:
            return None
        # Replace the first occurrence of the term with blank
        lowered = sentence.lower()
        term_lower = concept.term.lower()
        if term_lower in lowered:
            start_index = lowered.index(term_lower)
            end_index = start_index + len(term_lower)
            blanked = sentence[:start_index] + "_____" + sentence[end_index:]
        else:
            # If term not found, blank the longest word (as fallback)
            words = sentence.split()
            target = max(words, key=len)
            blanked = sentence.replace(target, "_____", 1)
            term_lower = target.lower()
        correct = concept.term if term_lower == concept.term.lower() else term_lower
        difficulty = self.difficulty.assess(
            importance_score=concept.importance_score, sentence_length=len(sentence.split())
        )
        return Question(
            type="fill_blank",
            text=blanked,
            options=None,
            correct_answer=str(correct),
            explanation=sentence,
            difficulty=difficulty,
            source_reference=sentence,
        )

    def _make_short_answer(self, concept: Concept) -> Optional[Question]:
        sentence = (concept.supporting_sentences or [""])[0]
        if not sentence:
            return None
        prompt = f"Explain '{concept.term}' in one or two sentences."
        correct = self._extract_definition_or_term(concept) or concept.term
        difficulty = self.difficulty.assess(
            importance_score=concept.importance_score, sentence_length=len(sentence.split())
        )
        return Question(
            type="short_answer",
            text=prompt,
            options=None,
            correct_answer=correct,
            explanation=sentence,
            difficulty=difficulty,
            source_reference=sentence,
        )

    def _extract_definition_or_term(self, concept: Concept) -> Optional[str]:
        if concept.definition_candidates:
            # Return definition fragment
            return concept.definition_candidates[0]
        return None