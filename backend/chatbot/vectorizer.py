"""
vectorizer.py
-------------
TF-IDF vectorisation layer for the Nexus Venture recommendation chatbot.

Responsibilities:
  - Fit a TfidfVectorizer on the startup corpus.
  - Transform startup and user/query feature strings into sparse vectors.
  - Expose a single `get_tfidf_vectors()` helper used by matcher.py.

FUTURE EXTENSION:
- Replace TfidfVectorizer with sentence-transformers (BERT / MiniLM) for
  semantic embeddings:
      from sentence_transformers import SentenceTransformer
      model = SentenceTransformer('all-MiniLM-L6-v2')
      embeddings = model.encode(texts)
- Store embeddings in FAISS for sub-millisecond ANN search at scale.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple


class NexusVectorizer:
    """
    Wraps sklearn's TfidfVectorizer with fit/transform helpers
    tailored for the Nexus Venture matching pipeline.
    """

    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
    ):
        """
        Parameters
        ----------
        max_features : vocabulary size cap (top N by TF-IDF weight)
        ngram_range  : unigrams + bigrams by default for richer matching
        """
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words="english",   # second-pass stopword removal
            sublinear_tf=True,      # apply log(1+tf) to dampen high-freq terms
        )
        self._fitted = False

    # ── Fit ───────────────────────────────────────────────────────────────────

    def fit(self, corpus: List[str]) -> None:
        """
        Fit the vectorizer on the startup corpus.
        Call this once when the chatbot initialises.
        """
        self.vectorizer.fit(corpus)
        self._fitted = True

    # ── Transform ─────────────────────────────────────────────────────────────

    def transform(self, texts: List[str]):
        """
        Transform a list of pre-processed text strings into a TF-IDF matrix.
        Returns a scipy sparse matrix of shape (len(texts), vocab_size).
        """
        if not self._fitted:
            raise RuntimeError("NexusVectorizer must be fitted before transform().")
        return self.vectorizer.transform(texts)

    def fit_transform(self, corpus: List[str]):
        """Fit and transform in one step (used for the startup corpus)."""
        self._fitted = True
        return self.vectorizer.fit_transform(corpus)

    # ── Similarity ────────────────────────────────────────────────────────────

    def cosine_scores(self, query_vec, corpus_matrix) -> np.ndarray:
        """
        Compute cosine similarity between a single query vector and
        every row in corpus_matrix.

        Returns a 1-D numpy array of shape (n_startups,).
        """
        scores = cosine_similarity(query_vec, corpus_matrix)
        return scores.flatten()


# ── Module-level convenience function ─────────────────────────────────────────

def get_tfidf_vectors(
    startup_features: List[str],
    query_feature: str,
) -> Tuple[object, object, NexusVectorizer]:
    """
    One-shot helper: fit on startup corpus, transform both startups and query.

    Parameters
    ----------
    startup_features : list of pre-processed startup feature strings
    query_feature    : pre-processed user/query feature string

    Returns
    -------
    (startup_matrix, query_vector, fitted_vectorizer).

    Note:
    - Matrices are returned as scipy sparse matrices (sklearn default),
      which is efficient for TF-IDF.
    """
    vec = NexusVectorizer()
    startup_matrix = vec.fit_transform(startup_features)
    query_vector   = vec.transform([query_feature])
    return startup_matrix, query_vector, vec
