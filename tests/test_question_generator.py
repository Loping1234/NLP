from quizgen import QuestionGenerator
from quizgen.text_analyzer import Concept
from quizgen.config import QuizConfig


def test_generate_questions():
    concepts = [
        Concept(
            term="machine learning",
            supporting_sentences=[
                "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
            ],
            definition_candidates=[
                "Machine learning is a subset of artificial intelligence"
            ],
            named_entities=[],
            numerical_facts=["2020"],
            importance_score=0.8,
        )
    ]
    gen = QuestionGenerator(random_seed=123)
    cfg = QuizConfig(num_mcq=1, num_true_false=1, num_fill_blank=1, num_short_answer=1)
    questions = gen.create_questions(concepts, cfg)
    assert len(questions) == 4