from models.content_based import ContentBasedFilter

cb = ContentBasedFilter()
cb.load_data()
cb.build_similarity()

# Test 1: Find movies similar to Toy Story
print("\n🎬 Movies similar to Toy Story (1995):")
recs = cb.recommend_by_title("Toy Story (1995)", top_n=5)
for i, r in enumerate(recs, 1):
    print(f"  {i}. {r['title']}  [{r['genres']}]  (score: {r['score']})")

# Test 2: Find movies similar to a thriller
print("\n🎬 Movies similar to The Dark Knight:")
recs2 = cb.recommend_by_title("Dark Knight, The (2008)", top_n=5)
for i, r in enumerate(recs2, 1):
    print(f"  {i}. {r['title']}  [{r['genres']}]  (score: {r['score']})")

# Test 3: Recommend based on User 1's watch history
print("\n🎬 Content-based recommendations for User 1:")
recs3 = cb.recommend_by_user_history(user_id=1, top_n=5)
for i, r in enumerate(recs3, 1):
    print(f"  {i}. {r['title']}  (score: {r['score']})")