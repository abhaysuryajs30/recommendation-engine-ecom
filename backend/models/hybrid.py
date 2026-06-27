import pandas as pd
from models.collaborative import CollaborativeFilter
from models.content_based import ContentBasedFilter
from cache.redis_cache import RecommendationCache

class HybridRecommender:
    def __init__(self, collab_weight=0.6, content_weight=0.4):
        self.collab_weight  = collab_weight
        self.content_weight = content_weight
        self.cf    = CollaborativeFilter()
        self.cb    = ContentBasedFilter()
        self.cache = RecommendationCache(use_real_redis=False, ttl_seconds=3600)

    def load_and_build(self):
        print("Loading collaborative filter...")
        self.cf.load_data()
        self.cf.build_matrix()
        self.cf.compute_similarity()
        print("\nLoading content-based filter...")
        self.cb.load_data()
        self.cb.build_similarity()
        print("\n✅ Hybrid recommender ready!")

    def recommend(self, user_id, top_n=10):
        # ── Check cache first ─────────────────────────────────────
        cached = self.cache.get_recommendations(user_id)
        if cached:
            return cached[:top_n]

        # ── Cache miss — calculate recommendations ────────────────
        collab_recs = self.cf.recommend(user_id, top_n=50)
        if collab_recs:
            max_c = max(r['score'] for r in collab_recs)
            for r in collab_recs:
                r['score'] = r['score'] / max_c if max_c > 0 else 0

        content_recs = self.cb.recommend_by_user_history(user_id, top_n=50)
        if isinstance(content_recs, dict):
            content_recs = []
        if content_recs:
            max_ct = max(r['score'] for r in content_recs)
            for r in content_recs:
                r['score'] = r['score'] / max_ct if max_ct > 0 else 0

        collab_dict  = {r['movieId']: r for r in collab_recs}
        content_dict = {r['movieId']: r for r in content_recs}
        all_movie_ids = set(collab_dict.keys()) | set(content_dict.keys())

        hybrid_scores = []
        for movie_id in all_movie_ids:
            c_score  = collab_dict[movie_id]['score']  if movie_id in collab_dict  else 0
            ct_score = content_dict[movie_id]['score'] if movie_id in content_dict else 0
            hybrid   = (self.collab_weight * c_score) + (self.content_weight * ct_score)
            info     = collab_dict.get(movie_id) or content_dict.get(movie_id)
            hybrid_scores.append({
                'movieId':       movie_id,
                'title':         info['title'],
                'collab_score':  round(c_score,  3),
                'content_score': round(ct_score, 3),
                'hybrid_score':  round(hybrid,   3)
            })

        hybrid_scores.sort(key=lambda x: x['hybrid_score'], reverse=True)
        result = hybrid_scores[:50]   # cache top 50, serve top N

        # ── Save to cache ─────────────────────────────────────────
        self.cache.set_recommendations(user_id, result)
        return result[:top_n]