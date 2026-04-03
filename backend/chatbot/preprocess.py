"""
preprocess.py
-------------
Text preprocessing pipeline for the Nexus Venture recommendation chatbot.

Steps applied:
  1. Lowercase
  2. Remove punctuation
  3. Remove English stopwords (sklearn)
  4. Optional lemmatization (only if NLTK is installed)

FUTURE EXTENSION:
- Swap NLTK lemmatizer for spaCy's lemmatizer for better accuracy.
- Add domain-specific stopwords (e.g. "startup", "company").
"""

import re
import string
from typing import Iterable, Optional

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_STOP_WORDS = set(ENGLISH_STOP_WORDS)


def _optional_wordnet_lemmatizer():
    """
    Best-effort lemmatizer loader.

    Why this exists:
    - NLTK is not a required dependency in this repo.
    - If NLTK (and wordnet data) are available, we can lemmatize.
    - Otherwise, we silently skip lemmatization to keep the system runnable.
    """
    try:
        from nltk.stem import WordNetLemmatizer  # type: ignore
        return WordNetLemmatizer()
    except Exception:
        return None


_LEMMATIZER = _optional_wordnet_lemmatizer()


# ── Core function ──────────────────────────────────────────────────────────────

def clean_text(text: str, lemmatize: bool = True) -> str:
    """
    Full preprocessing pipeline for a single text string.

    Parameters
    ----------
    text      : raw input string
    lemmatize : whether to apply WordNet lemmatization (default True)

    Returns
    -------
    Cleaned, normalised string ready for TF-IDF vectorisation.
    """
    if not isinstance(text, str):
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # 3. Remove punctuation and special characters (keep spaces)
    text = text.translate(str.maketrans("", "", string.punctuation))

    # 4. Remove digits
    text = re.sub(r"\d+", "", text)

    # 5. Tokenise on whitespace
    tokens = text.split()

    # 6. Remove stopwords
    tokens = [t for t in tokens if t not in _STOP_WORDS]

    # 7. Optional lemmatization (only when available)
    if lemmatize and _LEMMATIZER is not None:
        try:
            tokens = [_LEMMATIZER.lemmatize(t) for t in tokens]
        except Exception:
            # If NLTK data isn't present (wordnet), do not fail the request.
            pass

    return " ".join(tokens)


def build_startup_feature(row) -> str:
    """
    Combine startup fields into a single feature string for vectorisation.
    Formula: domain + description + problem_statement + required_skills + funding_stage
    """
    combined = " ".join([
        str(row.get("domain",            "")),
        str(row.get("description",       "")),
        str(row.get("problem_statement", "")),
        str(row.get("required_skills",   "")),
        str(row.get("funding_stage",     "")),
    ])
    return clean_text(combined)


def build_user_feature(row) -> str:
    """
    Combine user fields into a single feature string for vectorisation.
    Formula: skills + interests + experience_level + preferred_funding_stage
    """
    combined = " ".join([
        str(row.get("skills",                  "")),
        str(row.get("interests",               "")),
        str(row.get("experience_level",        "")),
        str(row.get("preferred_funding_stage", "")),
    ])
    return clean_text(combined)


def build_query_feature(query_dict: dict) -> str:
    """
    Build a feature string from a free-form user query dictionary.
    Accepts any combination of keys and concatenates their values.
    """
    combined = " ".join(str(v) for v in query_dict.values())
    return clean_text(combined)
