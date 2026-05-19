import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class MovieDataLoader:
    """
    Handles data loading, chronological sorting, and extraction 
    of user histories and item metadata from the dataset.
    """
    def __init__(self, file_path: str):
        # 1. Load the dataset
        self.df = pd.read_csv(file_path)
        
        # 2. Parse the date strings (e.g., '2002-01-26') safely into datetime objects
        self.df['time'] = pd.to_datetime(self.df['time'], errors='coerce')
        
        # 3. Sort chronologically so sequential/historical analysis functions correctly
        self.df = self.df.sort_values(by='time')

    def get_user_history(self, user_id: str, limit: int = 5) -> list:
        """
        Retrieves a chronological list of a user's past reviews 
        to build their historical behavioral profile context.
        """
        user_df = self.df[self.df['userId'] == user_id]
        if user_df.empty:
            return []
        
        history = []
        # Take the oldest reviews first to capture baseline profile habits
        for _, row in user_df.head(limit).iterrows():
            history.append({
                "title": row.get('title', 'Unknown'),
                "score": row.get('score', 3.0),
                "summary": row.get('summary', ''),
                "text": row.get('text', ''),
                "categories": row.get('categories', '')
            })
        return history

    def get_movie_metadata(self, product_id: str) -> dict:
        """
        Retrieves metadata properties for a specific item to serve 
        as contextual prompt details for evaluation.
        """
        movie_df = self.df[self.df['productId'] == product_id]
        if movie_df.empty:
            return None
            
        row = movie_df.iloc[0]
        return {
            "productId": product_id,
            "title": row.get('title', 'Unknown'),
            "categories": row.get('categories', ''),
            "description": row.get('description', 'No description available.'),
            "directors": row.get('directors', 'N/A'),
            "actors": row.get('actors', 'N/A')
        }

    def _ensure_vector_index(self):
        """
        Lazily builds a TF-IDF vector index over the catalog (title + description + categories).
        Cached on the instance for repeated queries.
        """
        if getattr(self, '_vectorizer', None) is not None:
            return

        # Construct a single text field per document for retrieval
        texts = (
            self.df.get('title', '').fillna('') + ' ' +
            self.df.get('description', '').fillna('') + ' ' +
            self.df.get('categories', '').fillna('')
        )

        self._doc_index = self.df.reset_index(drop=True)
        self._doc_texts = texts.fillna('').astype(str).tolist()

        self._vectorizer = TfidfVectorizer(stop_words='english', max_features=20000)
        # Fit on the whole corpus
        self._doc_vectors = self._vectorizer.fit_transform(self._doc_texts)

    def semantic_search(self, query: str, k: int = 10) -> list:
        """
        Returns up to `k` candidate items most similar to the free-text `query`.
        Uses TF-IDF + cosine similarity for a lightweight semantic fallback.
        """
        if not query:
            return []

        self._ensure_vector_index()

        q_vec = self._vectorizer.transform([query])
        sims = linear_kernel(q_vec, self._doc_vectors).flatten()

        # Get top-k document indices
        top_idx = np.argsort(sims)[::-1][:k]

        results = []
        for idx in top_idx:
            row = self._doc_index.iloc[idx]
            results.append({
                'productId': row.get('productId', ''),
                'title': row.get('title', ''),
                'description': row.get('description', ''),
                'categories': row.get('categories', ''),
                'score': float(row.get('score', 0)) if 'score' in row else None
            })

        return results