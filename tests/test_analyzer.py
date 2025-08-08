from quizgen import TextPreprocessor, ContentAnalyzer


def test_extract_concepts_basic():
    text = (
        "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. "
        "Supervised learning uses labeled data. Unsupervised learning finds patterns."
    )
    pre = TextPreprocessor()
    processed = pre.process(text)
    analyzer = ContentAnalyzer(pre)
    concepts = analyzer.extract_concepts(processed, max_terms=10)
    assert isinstance(concepts, list)
    assert len(concepts) > 0