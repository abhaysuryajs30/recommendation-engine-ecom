from models.hybrid import HybridRecommender

hr = HybridRecommender(collab_weight=0.6, content_weight=0.4)
hr.load_and_build()

# Test with User 1
print("\n🎬 Hybrid recommendations for User 1:")
print(f"{'Title':<45} {'Collab':>8} {'Content':>8} {'Hybrid':>8}")
print("-" * 73)
recs = hr.recommend(user_id=1, top_n=10)
for r in recs:
    print(f"{r['title']:<45} {r['collab_score']:>8} {r['content_score']:>8} {r['hybrid_score']:>8}")

# Test with User 50
print("\n🎬 Hybrid recommendations for User 50:")
print(f"{'Title':<45} {'Collab':>8} {'Content':>8} {'Hybrid':>8}")
print("-" * 73)
recs2 = hr.recommend(user_id=50, top_n=10)
for r in recs2:
    print(f"{r['title']:<45} {r['collab_score']:>8} {r['content_score']:>8} {r['hybrid_score']:>8}")

# Show the power of hybrid — movies that appear in BOTH signals
print("\n💡 Movies appearing in BOTH collaborative AND content signals (User 1):")
recs3 = hr.recommend(user_id=1, top_n=50)
both = [r for r in recs3 if r['collab_score'] > 0 and r['content_score'] > 0]
for r in both[:5]:
    print(f"  → {r['title']}  (collab: {r['collab_score']}, content: {r['content_score']}, hybrid: {r['hybrid_score']})")