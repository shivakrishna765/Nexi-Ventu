import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

def compute_similarity(query: str, documents: List[str]) -> List[float]:
    """
    Computes cosine similarity between a single query string and a list of document strings.
    Returns a list of floats representing the similarity scores (0.0 to 1.0).
    """
    if not query or not documents:
        return [0.0] * len(documents)
        
    # We include the query in the list of documents so the vectorizer learns its vocabulary
    # although in a large-scale system you'd fit on a large corpus separately.
    texts = [query] + documents
    
    # Initialize the TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        # Fit and transform the texts into TF-IDF vectors
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Calculate cosine similarity of the query (index 0) against all documents (index 1 to N)
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        return similarity_scores[0].tolist()
    except Exception as e:
        # If vectorization fails (e.g. all stop words), return zeros
        print(f"Error computing similarity: {e}")
        return [0.0] * len(documents)
