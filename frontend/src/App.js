import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API = "https://recommendation-engine-ecom.onrender.com";

function MovieCard({ movie, score }) {
  return (
    <div className="movie-card">
      <div className="movie-poster">
        <span className="movie-icon">🎬</span>
      </div>
      <div className="movie-info">
        <p className="movie-title">{movie.title}</p>
        {score && (
          <div className="score-row">
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${Math.round(score * 100)}%` }} />
            </div>
            <span className="score-label">{Math.round(score * 100)}%</span>
          </div>
        )}
        {movie.avg_rating && (
          <p className="movie-rating">⭐ {movie.avg_rating}</p>
        )}
        <p className="movie-genre">{movie.genres?.split("|").slice(0, 2).join(" · ")}</p>
      </div>
    </div>
  );
}

function App() {
  const [userId, setUserId]         = useState(1);
  const [recs, setRecs]             = useState([]);
  const [movies, setMovies]         = useState([]);
  const [genre, setGenre]           = useState("All");
  const [loading, setLoading]       = useState(false);
  const [cacheStatus, setCacheStatus] = useState("");

  const GENRES = ["All", "Action", "Comedy", "Drama", "Thriller", "Romance", "Animation"];
  const USERS  = [1, 5, 10, 20, 50, 100, 200];

  // Fetch recommendations when user changes
  useEffect(() => {
    const fetchRecs = async () => {
      setLoading(true);
      setCacheStatus("");
      try {
        const start = Date.now();
        const res = await axios.get(`${API}/recommend/${userId}?top_n=8`);
        const elapsed = Date.now() - start;
        setRecs(res.data.recommendations);
        setCacheStatus(elapsed < 50 ? `⚡ Cache hit — ${elapsed}ms` : `🔄 Calculated — ${elapsed}ms`);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    fetchRecs();
  }, [userId]);

  // Fetch movies when genre changes
  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const url = genre === "All"
          ? `${API}/movies?limit=12`
          : `${API}/movies?genre=${genre}&limit=12`;
        const res = await axios.get(url);
        setMovies(res.data.movies);
      } catch (err) {
        console.error(err);
      }
    };
    fetchMovies();
  }, [genre]);

  const clearCache = async () => {
    await axios.delete(`${API}/cache/${userId}`);
    setCacheStatus("🗑️ Cache cleared — next request will recalculate");
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <span className="logo">🎬 CineRec</span>
          <span className="tagline">Hybrid Recommendation Engine</span>
        </div>
        <div className="header-right">
          <span className="user-label">Viewing as User</span>
          <select
            className="user-select"
            value={userId}
            onChange={e => setUserId(Number(e.target.value))}
          >
            {USERS.map(u => <option key={u} value={u}>User {u}</option>)}
          </select>
        </div>
      </header>

      <main className="main">
        {/* Recommendations Section */}
        <section className="section">
          <div className="section-header">
            <div className="section-title-row">
              <h2 className="section-title">✨ Recommended for you</h2>
              <span className="badge">Hybrid model</span>
            </div>
            <div className="cache-row">
              {cacheStatus && <span className="cache-status">{cacheStatus}</span>}
              <button className="clear-btn" onClick={clearCache}>Clear cache</button>
            </div>
          </div>

          {loading ? (
            <div className="loading">Calculating recommendations...</div>
          ) : (
            <div className="movie-grid">
              {recs.map(rec => (
                <MovieCard
                  key={rec.movieId}
                  movie={{ title: rec.title, genres: "" }}
                  score={rec.hybrid_score}
                />
              ))}
            </div>
          )}
        </section>

        {/* Score Breakdown for top pick */}
        {recs.length > 0 && (
          <section className="section breakdown-section">
            <h2 className="section-title">🔍 Score breakdown — top pick</h2>
            <div className="breakdown-card">
              <p className="breakdown-title">{recs[0].title}</p>
              <div className="breakdown-rows">
                <div className="breakdown-row">
                  <span className="breakdown-label">👥 Collaborative</span>
                  <div className="score-bar wide">
                    <div className="score-fill collab" style={{ width: `${Math.round(recs[0].collab_score * 100)}%` }} />
                  </div>
                  <span className="score-num">{Math.round(recs[0].collab_score * 100)}%</span>
                </div>
                <div className="breakdown-row">
                  <span className="breakdown-label">🎭 Content</span>
                  <div className="score-bar wide">
                    <div className="score-fill content" style={{ width: `${Math.round(recs[0].content_score * 100)}%` }} />
                  </div>
                  <span className="score-num">{Math.round(recs[0].content_score * 100)}%</span>
                </div>
                <div className="breakdown-row">
                  <span className="breakdown-label">⚡ Hybrid (0.6·C + 0.4·CB)</span>
                  <div className="score-bar wide">
                    <div className="score-fill hybrid" style={{ width: `${Math.round(recs[0].hybrid_score * 100)}%` }} />
                  </div>
                  <span className="score-num">{Math.round(recs[0].hybrid_score * 100)}%</span>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Browse All Movies */}
        <section className="section">
          <div className="section-header">
            <h2 className="section-title">🎥 Browse movies</h2>
            <div className="genre-filters">
              {GENRES.map(g => (
                <button
                  key={g}
                  className={`genre-btn ${genre === g ? "active" : ""}`}
                  onClick={() => setGenre(g)}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
          <div className="movie-grid">
            {movies.map(movie => (
              <MovieCard key={movie.movieId} movie={movie} />
            ))}
          </div>
        </section>
      </main>

      <footer className="footer">
        Powered by collaborative filtering + content-based filtering · FastAPI + React
      </footer>
    </div>
  );
}

export default App;