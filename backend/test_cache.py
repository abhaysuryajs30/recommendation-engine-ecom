import time
from models.hybrid import HybridRecommender

hr = HybridRecommender()
hr.load_and_build()

print("\n" + "="*55)
print("CACHE PERFORMANCE TEST")
print("="*55)

# First request — cache miss, will calculate
print("\nRequest 1 (cold):")
t1 = time.time()
recs = hr.recommend(user_id=1, top_n=5)
t1_end = time.time()
print(f"  ⏱  Time: {(t1_end - t1)*1000:.0f}ms")
print(f"  Top pick: {recs[0]['title']}")

# Second request — cache hit, instant
print("\nRequest 2 (cached):")
t2 = time.time()
recs2 = hr.recommend(user_id=1, top_n=5)
t2_end = time.time()
print(f"  ⏱  Time: {(t2_end - t2)*1000:.0f}ms")
print(f"  Top pick: {recs2[0]['title']}")

elapsed_cached = (t2_end - t2)
if elapsed_cached > 0:
    speedup = (t1_end - t1) / elapsed_cached
    print(f"\n🚀 Cache made request 2 → {speedup:.0f}x faster")
else:
    print(f"\n🚀 Cache made request 2 → effectively instant (sub-millisecond)")

# Invalidate and re-request
print("\nInvalidating cache for user 1...")
hr.cache.invalidate(user_id=1)

print("\nRequest 3 (after invalidation — cold again):")
t3 = time.time()
recs3 = hr.recommend(user_id=1, top_n=5)
t3_end = time.time()
print(f"  ⏱  Time: {(t3_end - t3)*1000:.0f}ms")
print(f"  Top pick: {recs3[0]['title']}")