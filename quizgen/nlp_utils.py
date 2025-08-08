from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


@dataclass
class ProcessedText:
    sentences: List[str]
    tokens_by_sentence: List[List[str]]


class TextPreprocessor:
    def __init__(self, language_code: str = "english") -> None:
        self.language_code = language_code
        try:
            self.stop_words = set(stopwords.words(language_code))
        except LookupError:
            self.stop_words = set()

        # Optional spaCy support
        self.spacy_nlp = None
        try:
            import spacy
            try:
                self.spacy_nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.spacy_nlp = spacy.blank("en")
        except Exception:
            self.spacy_nlp = None

    def process(self, text: str) -> ProcessedText:
        sentences = self._sentence_tokenize(text)
        tokens_by_sentence = [self._word_tokenize(s) for s in sentences]
        return ProcessedText(sentences=sentences, tokens_by_sentence=tokens_by_sentence)

    def _sentence_tokenize(self, text: str) -> List[str]:
        try:
            sentences = sent_tokenize(text)
            return [s.strip() for s in sentences if s.strip()]
        except LookupError:
            # Fallback regex split
            return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    def _word_tokenize(self, sentence: str) -> List[str]:
        try:
            tokens = word_tokenize(sentence)
        except LookupError:
            tokens = re.findall(r"\b\w+\b", sentence)
        tokens = [t.lower() for t in tokens]
        tokens = [t for t in tokens if t.isalpha() and t not in self.stop_words]
        return tokens

    def pos_tag(self, tokens: List[str]) -> List[tuple[str, str]]:
        try:
            return nltk.pos_tag(tokens)
        except LookupError:
            return [(t, "NN") for t in tokens]

    def named_entities(self, text: str) -> List[str]:
        if self.spacy_nlp is None:
            return []
        doc = self.spacy_nlp(text)
        return list({ent.text for ent in doc.ents})