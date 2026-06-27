import pandas as pd
import os

# Load data
ratings = pd.read_csv('data/ratings.csv')
movies  = pd.read_csv('data/movies.csv')

print("=== RATINGS ===")
print(ratings.head())
print(f"\nTotal ratings : {ratings.shape[0]}")
print(f"Unique users  : {ratings['userId'].nunique()}")
print(f"Unique movies : {ratings['movieId'].nunique()}")

print("\n=== MOVIES ===")
print(movies.head())
print(f"\nSample genre  : {movies['genres'].iloc[0]}")

print("\n=== RATINGS DISTRIBUTION ===")
print(ratings['rating'].value_counts().sort_index())

print("\n✅ Data loaded successfully! Ready for Step 2.")