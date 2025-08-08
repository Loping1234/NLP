from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from .nlp_utils import ProcessedText, TextPreprocessor


@dataclass
class Concept:
    term: str
    supporting_sentences: List[str]
    definition_candidates: List[str]
    named_entities: List[str]
    numerical_facts: List[str]
    importance_score: float


class ContentAnalyzer:
    def __init__(self, preprocessor: Optional[TextPreprocessor] = None) -> None:
        self.preprocessor = preprocessor or TextPreprocessor()

    def extract_concepts(self, processed: ProcessedText, max_terms: int = 50) -> List[Concept]:
        sentences = processed.sentences
        documents_tokens = processed.tokens_by_sentence
        if not documents_tokens:
            return []

        # Build documents with unigrams + bigrams
        documents: List[List[str]] = []
        for tokens in documents_tokens:
            bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
            documents.append(tokens + bigrams)

        term_scores = self._compute_tfidf_scores(documents)
        # Pick top terms as candidate concepts
        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        top_terms = [t for t, _ in sorted_terms[:max_terms]]

        # Map terms to supporting sentences
        term_to_sentences: Dict[str, List[str]] = {t: [] for t in top_terms}
        for sent in sentences:
            sent_lower = sent.lower()
            for t in top_terms:
                if re.search(rf"\b{re.escape(t)}\b", sent_lower):
                    term_to_sentences[t].append(sent)

        # Extract definitions and numbers
        concept_list: List[Concept] = []
        full_text = " ".join(sentences)
        named_entities = self.preprocessor.named_entities(full_text)
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", full_text)

        for term in top_terms:
            sents = term_to_sentences.get(term, [])
            defs = [s for s in sents if self._looks_like_definition(term, s)]
            concept_list.append(
                Concept(
                    term=term,
                    supporting_sentences=sents[:5],
                    definition_candidates=defs,
                    named_entities=named_entities,
                    numerical_facts=numbers,
                    importance_score=term_scores.get(term, 0.0),
                )
            )
        return concept_list

    def _compute_tfidf_scores(self, documents: List[List[str]]) -> Dict[str, float]:
        # Compute document frequency
        num_docs = len(documents)
        df: Dict[str, int] = {}
        for doc in documents:
            seen = set(doc)
            for term in seen:
                df[term] = df.get(term, 0) + 1
        # Compute mean TF-IDF across documents
        term_sum_tfidf: Dict[str, float] = {}
        for doc in documents:
            if not doc:
                continue
            length = float(len(doc))
            tf: Dict[str, float] = {}
            for term in doc:
                tf[term] = tf.get(term, 0.0) + 1.0 / length
            for term, tf_val in tf.items():
                idf = 1.0 + (0.0 if df.get(term, 0) == 0 else 
                             max(0.0, (num_docs + 1) / (df[term] + 1)))
                # Use log smoothing for idf
                import math
                idf = 1.0 + math.log((num_docs + 1) / (df[term] + 1))
                term_sum_tfidf[term] = term_sum_tfidf.get(term, 0.0) + tf_val * idf
        # Mean across documents
        return {term: total / num_docs for term, total in term_sum_tfidf.items()}

    def _looks_like_definition(self, term: str, sentence: str) -> bool:
        term_re = re.escape(term)
        patterns = [
            rf"\b{term_re}\s+is\s+(an|a|the)\b",
            rf"\b{term_re}\s+refers\s+to\b",
            rf"\b{term_re}\s+can\s+be\s+defined\s+as\b",
        ]
        sent_lower = sentence.lower()
        return any(re.search(p, sent_lower) for p in patterns)