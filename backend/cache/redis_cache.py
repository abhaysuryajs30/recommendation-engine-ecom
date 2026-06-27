import json
import time

class MockRedis:
    """
    Simulates Redis in memory during development.
    Same API as real Redis — swap it out with redis.Redis() for production.
    Structure: { key: { 'value': ..., 'expires_at': timestamp } }
    """
    def __init__(self):
        self._store = {}

    def get(self, key):
        if key in self._store:
            entry = self._store[key]
            # Check if expired
            if entry['expires_at'] is None or time.time() < entry['expires_at']:
                return entry['value'].encode()   # mimic real Redis bytes response
            else:
                del self._store[key]             # expired, remove it
        return None

    def setex(self, key, seconds, value):
        self._store[key] = {
            'value': value,
            'expires_at': time.time() + seconds
        }

    def delete(self, key):
        self._store.pop(key, None)

    def exists(self, key):
        return key in self._store


class RecommendationCache:
    def __init__(self, use_real_redis=False, ttl_seconds=3600):
        """
        ttl_seconds = how long to keep cached recommendations
        3600 = 1 hour (good default for recommendations)
        """
        self.ttl = ttl_seconds

        if use_real_redis:
            # For production — requires Redis server running
            import redis
            self.client = redis.Redis(host='localhost', port=6379, db=0)
            print("✅ Connected to real Redis")
        else:
            # For development — no Redis server needed
            self.client = MockRedis()
            print("✅ Using in-memory cache (MockRedis)")

    def get_recommendations(self, user_id):
        """Check cache for existing recommendations."""
        key = f"recs:user:{user_id}"
        cached = self.client.get(key)

        if cached:
            print(f"  🟢 Cache HIT for user {user_id}")
            return json.loads(cached.decode())

        print(f"  🔴 Cache MISS for user {user_id} — will calculate")
        return None

    def set_recommendations(self, user_id, recommendations):
        """Save recommendations to cache."""
        key = f"recs:user:{user_id}"
        self.client.setex(key, self.ttl, json.dumps(recommendations))
        print(f"  💾 Cached recommendations for user {user_id} ({self.ttl}s TTL)")

    def invalidate(self, user_id):
        """Clear cache for a user (e.g. after they rate a new movie)."""
        key = f"recs:user:{user_id}"
        self.client.delete(key)
        print(f"  🗑️  Cache cleared for user {user_id}")