from models.collaborative import CollaborativeFilter

cf = CollaborativeFilter()
cf.load_data()
cf.build_matrix()
cf.compute_similarity()

# Test with User 1
print("\n🎬 Top 10 recommendations for User 1:")
recs = cf.recommend(user_id=1, top_n=10)
for i, rec in enumerate(recs, 1):
    print(f"  {i}. {rec['title']}  (score: {rec['score']})")

# Test with another user to verify it gives different results
print("\n🎬 Top 10 recommendations for User 50:")
recs2 = cf.recommend(user_id=50, top_n=10)
for i, rec in enumerate(recs2, 1):
    print(f"  {i}. {rec['title']}  (score: {rec['score']})")