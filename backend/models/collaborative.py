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
        self.ratings = pd.read_csv('data/ratings.csv')
        self.movies  = pd.read_csv('data/movies.csv')
        print(f"✅ Loaded {len(self.ratings)} ratings")

    def build_matrix(self):
        # Keep only top 200 most active users and top 500 most rated movies
        # Reduces memory from ~500MB to ~50MB — fits Render free tier
        top_users = (
            self.ratings.groupby('userId')['movieId']
            .count()
            .nlargest(200)
            .index
        )
        top_movies = (
            self.ratings.groupby('movieId')['userId']
            .count()
            .nlargest(500)
            .index
        )

        filtered = self.ratings[
            self.ratings['userId'].isin(top_users) &
            self.ratings['movieId'].isin(top_movies)
        ]

        self.user_item_matrix = filtered.pivot_table(
            index='userId',
            columns='movieId',
            values='rating'
        ).fillna(0)

        print(f"✅ Matrix shape: {self.user_item_matrix.shape}")

    def compute_similarity(self):
        self.user_similarity = cosine_similarity(self.user_item_matrix)
        self.user_similarity = pd.DataFrame(
            self.user_similarity,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index
        )
        print(f"✅ Similarity matrix shape: {self.user_similarity.shape}")

    def recommend(self, user_id, top_n=10):
        # If user not in reduced matrix, return empty
        if user_id not in self.user_similarity.index:
            return []

        similar_users = (
            self.user_similarity[user_id]
            .sort_values(ascending=False)
            .iloc[1:6]
            .index.tolist()
        )

        user_seen = set(
            self.ratings[self.ratings['userId'] == user_id]['movieId']
        )

        recommendations = {}
        for sim_user in similar_users:
            sim_score = self.user_similarity[user_id][sim_user]
            sim_user_ratings = self.ratings[
                (self.ratings['userId'] == sim_user) &
                (self.ratings['rating'] >= 4.0)
            ]
            for _, row in sim_user_ratings.iterrows():
                movie_id = row['movieId']
                if movie_id not in user_seen:
                    weighted = row['rating'] * sim_score
                    if movie_id in recommendations:
                        recommendations[movie_id] += weighted
                    else:
                        recommendations[movie_id] = weighted

        top_movie_list = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        results = []
        for movie_id, score in top_movie_list:
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