import pandas as pd

# Load ratings and runtimes
ratings_df = pd.read_csv('data/title.ratings.tsv', sep='\t')
runtime_df = pd.read_csv('data/title.basics.tsv', sep='\t', usecols=['tconst', 'runtimeMinutes'])

def safe_runtime(val):
    try:
        return int(val)
    except:
        return 90
runtime_df['runtimeMinutes'] = runtime_df['runtimeMinutes'].apply(lambda x: safe_runtime(x) if str(x).isdigit() else 90)

# Merge ratings and runtime info
movies_df = pd.merge(ratings_df, runtime_df, on='tconst', how='inner')
movie_ids = movies_df['tconst'].tolist()
runtimes_dict = {row['tconst']: row['runtimeMinutes'] for _, row in movies_df.iterrows()}

print(f"Number of movies in movie_ids: {len(movie_ids)}")
if movies_df.empty:
    print("movies_df is empty!")
elif len(movies_df) < 10:
    print(f"movies_df is very small: only {len(movies_df)} rows.")
else:
    print(f"movies_df has {len(movies_df)} rows.")

# Print statistics for runtimeMinutes and averageRating
print("\nStatistics for runtimeMinutes:")
print(f"Min: {movies_df['runtimeMinutes'].min()}")
print(f"Max: {movies_df['runtimeMinutes'].max()}")
print(f"Mean: {movies_df['runtimeMinutes'].mean():.2f}")

print("\nStatistics for averageRating:")
print(f"Min: {movies_df['averageRating'].min()}")
print(f"Max: {movies_df['averageRating'].max()}")
print(f"Mean: {movies_df['averageRating'].mean():.2f}")

# Print runtime distribution
import collections
runtime_counts = collections.Counter(runtimes_dict.values())
print("Runtime distribution (minutes):")
for runtime, count in sorted(runtime_counts.items()):
    print(f"{runtime}: {count}")
