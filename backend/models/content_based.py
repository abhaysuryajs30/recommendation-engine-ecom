import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedFilter:
    def __init__(self):
        self.movies = None
        self.ratings = None
        self.tfidf_matrix = None
        self.content_similarity = None
        self.movie_indices = None

    def load_data(self):
        self.movies  = pd.read_csv('data/movies.csv')
        self.ratings = pd.read_csv('data/ratings.csv')
        print(f"✅ Loaded {len(self.movies)} movies")

    def build_similarity(self):
        # Step 1: Clean genres — replace pipe | with space
        # "Action|Comedy|Drama" → "Action Comedy Drama"
        # TF-IDF needs space-separated words, not pipe-separated
        self.movies['genres_clean'] = (
            self.movies['genres']
            .str.replace('|', ' ', regex=False)
            .str.replace('-', ' ', regex=False)  # "Sci-Fi" → "Sci Fi"
        )

        # Step 2: Build TF-IDF matrix
        # Each movie becomes a vector of genre weights
        # Movies with same genres will have similar vectors
        tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = tfidf.fit_transform(self.movies['genres_clean'])

        print(f"✅ TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        # Expected: (9742, N) where N = number of unique genre words

        # Step 3: Compute cosine similarity between every pair of movies
        self.content_similarity = cosine_similarity(
            self.tfidf_matrix, self.tfidf_matrix
        )

        # Step 4: Create a lookup: movie title → row index in matrix
        self.movie_indices = pd.Series(
            self.movies.index,
            index=self.movies['title']
        )

        print(f"✅ Content similarity matrix shape: {self.content_similarity.shape}")
        # Expected: (9742, 9742)

    def recommend_by_title(self, title, top_n=10):
        # Find the row index for this movie
        if title not in self.movie_indices:
            return {"error": f"Movie '{title}' not found"}

        idx = self.movie_indices[title]

        # Get similarity scores for this movie vs all others
        sim_scores = list(enumerate(self.content_similarity[idx]))

        # Sort by similarity, skip index 0 (the movie itself)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]

        # Return movie titles and scores
        results = []
        for i, score in sim_scores:
            results.append({
                'movieId': int(self.movies.iloc[i]['movieId']),
                'title': self.movies.iloc[i]['title'],
                'genres': self.movies.iloc[i]['genres'],
                'score': round(float(score), 3)
            })
        return results

    def recommend_by_user_history(self, user_id, top_n=10):
        # Find movies this user rated highly (4.0+)
        user_highly_rated = self.ratings[
            (self.ratings['userId'] == user_id) &
            (self.ratings['rating'] >= 4.0)
        ]['movieId'].tolist()

        if not user_highly_rated:
            return {"error": "No highly rated movies found for this user"}

        # Get content-based recs for each highly-rated movie
        # then aggregate scores
        aggregated = {}
        user_seen = set(
            self.ratings[self.ratings['userId'] == user_id]['movieId']
        )

        for movie_id in user_highly_rated[:5]:  # Use top 5 to keep it fast
            title_match = self.movies[self.movies['movieId'] == movie_id]['title']
            if title_match.empty:
                continue
            title = title_match.values[0]
            recs = self.recommend_by_title(title, top_n=20)
            if isinstance(recs, dict):  # error case
                continue
            for rec in recs:
                mid = rec['movieId']
                if mid not in user_seen:
                    if mid in aggregated:
                        aggregated[mid]['score'] += rec['score']
                    else:
                        aggregated[mid] = rec.copy()

        # Sort and return top N
        sorted_recs = sorted(
            aggregated.values(),
            key=lambda x: x['score'],
            reverse=True
        )[:top_n]

        return sorted_recs