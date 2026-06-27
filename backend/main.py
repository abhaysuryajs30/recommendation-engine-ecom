from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd

from models.hybrid import HybridRecommender

# ── Global model instance ─────────────────────────────────────────────
# Loaded once at startup, shared across all requests
recommender = None
ratings_df  = None
movies_df   = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once when server starts — load heavy models here."""
    global recommender, ratings_df, movies_df

    print("🚀 Server starting — loading recommendation engine...")
    recommender = HybridRecommender(collab_weight=0.6, content_weight=0.4)
    recommender.load_and_build()

    # Also keep dataframes handy for the /movies endpoint
    ratings_df = pd.read_csv('data/ratings.csv')
    movies_df  = pd.read_csv('data/movies.csv')

    print("✅ Server ready!\n")
    yield
    # Anything after yield runs on shutdown (cleanup)
    print("Server shutting down...")

# ── Create FastAPI app ────────────────────────────────────────────────
app = FastAPI(
    title="Movie Recommendation Engine",
    description="Hybrid collaborative + content-based recommender system",
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS — allows React frontend to call this API ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "Recommendation Engine API",
        "docs":    "http://localhost:8000/docs",
        "endpoints": ["/recommend/{user_id}", "/movies", "/movie/{movie_id}", "/health"]
    }

@app.get("/health")
def health():
    """Health check — used by deployment pipelines to verify server is up."""
    return {"status": "ok", "model_loaded": recommender is not None}

@app.get("/recommend/{user_id}")
def get_recommendations(user_id: int, top_n: int = 10):
    """
    Get hybrid recommendations for a user.
    - user_id: integer (1–610 in MovieLens dataset)
    - top_n: how many recommendations to return (default 10)
    """
    if recommender is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    # Validate user exists
    valid_users = ratings_df['userId'].unique()
    if user_id not in valid_users:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found. Valid range: 1–610"
        )

    recs = recommender.recommend(user_id=user_id, top_n=top_n)
    return {
        "user_id": user_id,
        "count":   len(recs),
        "recommendations": recs
    }

@app.get("/movies")
def get_movies(limit: int = 20, genre: str = None):
    """
    Get list of movies, optionally filtered by genre.
    Example: /movies?genre=Action&limit=10
    """
    df = movies_df.copy()

    if genre:
        df = df[df['genres'].str.contains(genre, case=False, na=False)]

    movies = df.head(limit)[['movieId', 'title', 'genres']].to_dict(orient='records')
    return {"count": len(movies), "movies": movies}

@app.get("/movie/{movie_id}")
def get_movie_detail(movie_id: int):
    """Get details + average rating for a specific movie."""
    movie = movies_df[movies_df['movieId'] == movie_id]
    if movie.empty:
        raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")

    avg_rating = ratings_df[ratings_df['movieId'] == movie_id]['rating'].mean()
    rating_count = ratings_df[ratings_df['movieId'] == movie_id].shape[0]

    return {
        "movieId":      int(movie_id),
        "title":        movie['title'].values[0],
        "genres":       movie['genres'].values[0],
        "avg_rating":   round(float(avg_rating), 2) if not pd.isna(avg_rating) else None,
        "rating_count": int(rating_count)
    }

@app.delete("/cache/{user_id}")
def clear_cache(user_id: int):
    """Clear cached recommendations for a user (call after they rate a new movie)."""
    recommender.cache.invalidate(user_id)
    return {"message": f"Cache cleared for user {user_id}"}