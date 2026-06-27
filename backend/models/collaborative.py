import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeFilter:
    def __init__(self):
        self.ratings = None
        self.movies = None
        self.user_item_matrix = None
        self.user_similarity = None

    def load_data(self):
        # Load CSVs — ratings + movie titles
        self.ratings = pd.read_csv('data/ratings.csv')
        self.movies  = pd.read_csv('data/movies.csv')
        print(f"✅ Loaded {len(self.ratings)} ratings")

    def build_matrix(self):
        # Step 1: Pivot into user-item matrix
        # Rows = users, Columns = movies, Values = ratings
        # Empty cells (not watched) = 0
        self.user_item_matrix = self.ratings.pivot_table(
            index='userId',
            columns='movieId',
            values='rating'
        ).fillna(0)

        print(f"✅ Matrix shape: {self.user_item_matrix.shape}")
        # Expected: (610, 9724) — 610 users, 9724 movies

    def compute_similarity(self):
        # Step 2: Compute cosine similarity between every pair of users
        # Result is a 610x610 matrix
        # similarity[i][j] = how similar user i is to user j (0 to 1)
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity = pd.DataFrame(
            self.user_similarity,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        print(f"✅ Similarity matrix shape: {self.user_similarity.shape}")
        # Expected: (610, 610)

    def recommend(self, user_id, top_n=10):
        # Step 3: For a given user, find their top 5 most similar users
        similar_users = (
            self.user_similarity[user_id]
            .sort_values(ascending=False)
            .iloc[1:6]          # Skip index 0 — that's the user themselves
            .index.tolist()
        )

        # Step 4: Get movies those similar users rated highly (4.0+)
        # that our target user hasn't seen yet
        user_seen = set(
            self.ratings[self.ratings['userId'] == user_id]['movieId']
        )

        recommendations = {}
        for sim_user in similar_users:
            sim_score = self.user_similarity[user_id][sim_user]
            # Get highly rated movies by this similar user
            sim_user_ratings = self.ratings[
                (self.ratings['userId'] == sim_user) &
                (self.ratings['rating'] >= 4.0)
            ]
            for _, row in sim_user_ratings.iterrows():
                movie_id = row['movieId']
                if movie_id not in user_seen:
                    # Weight the rating by how similar this user is
                    weighted = row['rating'] * sim_score
                    if movie_id in recommendations:
                        recommendations[movie_id] += weighted
                    else:
                        recommendations[movie_id] = weighted

        # Step 5: Sort by score, get top N, attach movie titles
        top_movies = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        # Convert movieIds to titles
        results = []
        for movie_id, score in top_movies:
            title = self.movies[
                self.movies['movieId'] == movie_id
            ]['title'].values
            if len(title) > 0:
                results.append({
                    'movieId': int(movie_id),
                    'title': title[0],
                    'score': round(float(score), 3)
                })

        return results