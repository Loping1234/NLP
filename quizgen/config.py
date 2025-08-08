from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class QuizConfig:
    # Number of questions by type
    num_mcq: int = 5
    num_true_false: int = 5
    num_fill_blank: int = 5
    num_short_answer: int = 3

    # Difficulty distribution target (sum approx 1.0)
    difficulty_distribution: Dict[str, float] = field(
        default_factory=lambda: {"easy": 0.5, "medium": 0.35, "hard": 0.15}
    )

    # Topic filters (optional keywords)
    topic_keywords: Optional[List[str]] = None

    # Output options
    include_answers: bool = True
    max_options_per_mcq: int = 4

    # Formatting
    output_format: str = "json"  # json|text|pdf

    # Random seed for reproducibility
    random_seed: int = 42