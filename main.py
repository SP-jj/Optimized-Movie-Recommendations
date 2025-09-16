# This program recommends the best movies to watch, based on their average viewer ratings, and subject
#  to the following constraints:
#  1) A fixed number of movies must be recommended (TOTAL_RECOMMENDATIONS)
#  2) Each recommended movie will be within +/- PREF_TOLERANCE minutes of a preferred runtime (PREF_RUNTIME)
#  3) Each genre can only appear on up to GENRE_MAX times in the recommended list   !!TODO!!
#  4) Movies featuring a preferred actor/director will be favoured !!TODO!!
# 
#  Before running, ensure you have a solver installed that can handle integer programs, e.g., Gurobi, GLPK, CBC, etc., and enter its name in the SOLVER variable.
SOLVER = 'gurobi'

import pandas as pd
from pyomo.environ import *
import random

# Preferences
# Set number of recommendations constraint
TOTAL_RECOMMENDATIONS = 10
# Each recommended movie will be within +/-30 min of PREF_RUNTIME
PREF_RUNTIME = 80  # Preferred runtime for each movie
PREF_TOLERANCE = 20  # Tolerance for preferred runtime

# Maximum number of times a genre can appear in the recommendations
GENRE_MAX = 2


# List of data files
data_files = [
    "name.basics.tsv",
    "title.akas.tsv",
    "title.basics.tsv",
    "title.principals.tsv",
    "title.ratings.tsv"
]
data_dir = "data"


# Load movie ratings
ratings_path = f"{data_dir}/title.ratings.tsv"
ratings_df = pd.read_csv(ratings_path, sep='\t')

# Load movie runtimes and genres(a list of up to 3 strings). only cols are tconst, runtimeMinutes, and genres
basics_path = f"{data_dir}/title.basics.tsv"
movie_details_df = pd.read_csv(basics_path, sep='\t', usecols=['tconst', 'runtimeMinutes', 'genres'])

# Load movie names
akas_path = f"{data_dir}/title.akas.tsv"
akas_df = pd.read_csv(akas_path, sep='\t', usecols=['titleId','title'])
akas_df = akas_df.rename(columns={'titleId': 'tconst'})

# Build runtimes_dict: assign 90 with variance if runtimeMinutes is not an integer
def safe_runtime(val):
    try:
        return int(val)
    except:
        return random.randint(90,120)
movie_details_df['runtimeMinutes'] = movie_details_df['runtimeMinutes'].apply(lambda x: safe_runtime(x) if str(x).isdigit() else 90)

#Build genres_dict: assign empty list if genres is missing
def safe_genres(val):
    if pd.isna(val):
        return []
    return str(val).split(',')

movie_details_df['genres'] = movie_details_df['genres'].apply(safe_genres)

# Merge ratings, runtime info, and titles
movies_df = pd.merge(akas_df, pd.merge(ratings_df, movie_details_df, on='tconst', how='inner'),on='tconst', how='inner')
movie_ids = movies_df['tconst'].tolist()


# Create a Pyomo model
model = ConcreteModel()


# Boolean variable for each movie: 1 if recommended, 0 otherwise
model.x = Var(movie_ids, domain=Binary)


# Precompute ratings and runtimes as dictionaries for fast lookup
ratings_dict = {row['tconst']: row['averageRating'] for _, row in movies_df.iterrows()}
runtimes_dict = {row['tconst']: row['runtimeMinutes'] for _, row in movies_df.iterrows()}
genres_dict = {row['tconst']: row['genres'] for _, row in movies_df.iterrows()}

# Objective: maximize sum of averageRating for recommended movies
model.obj = Objective(
    expr=sum(model.x[m] * ratings_dict[m] for m in movie_ids),
    sense=maximize
)



# Total recommendations constraint: total number of recommended movies == TOTAL_RECOMMENDATIONS
def recommendations_constraint_rule(model):
    return sum(model.x[m] for m in movie_ids) == TOTAL_RECOMMENDATIONS
model.recommendations_constraint = Constraint(rule=recommendations_constraint_rule)

# constrains range of recommended movies to within +/- PREF_TOLERANCE of PREF_RUNTIME
def preferred_runtime_lower_rule(model, m):
    M = 10000
    return runtimes_dict[m] >= PREF_RUNTIME - PREF_TOLERANCE -(1 - model.x[m]) * M
def preferred_runtime_upper_rule(model, m):
    M = 10000
    return model.x[m] * runtimes_dict[m] <= PREF_RUNTIME + PREF_TOLERANCE
model.preferred_runtime_lower_constraint = Constraint(movie_ids, rule=preferred_runtime_lower_rule)
model.preferred_runtime_upper_constraint = Constraint(movie_ids, rule=preferred_runtime_upper_rule)

all_genres = {g for lst in genres_dict.values() for g in lst}

# # constrains each genre so that an instance of it appears in at most GENRE_MAX recommendations
# def genre_limit_rule(model,m, g):
#     return sum(model.x[m] for m in movie_ids if g in genres_dict[m]) <= 2

# model.genre_limit = Constraint(movie_ids, all_genres, rule=genre_limit_rule)

# Solve the model using the given solver
solver = SolverFactory(SOLVER)
result = solver.solve(model)

# Print recommended movies
print("Recommended movies:")
selected = []
for m in movie_ids:
    if model.x[m].value is not None and round(model.x[m].value) == 1:
        info = movies_df[movies_df['tconst'] == m].iloc[0]
        selected.append((m, info['averageRating'], info['runtimeMinutes'], info['genres']))
        print(f"ID: {m}, Rating: {info['averageRating']}, Runtime: {info['runtimeMinutes']} min, Genres: {info['genres']}")
total_runtime = sum(x[2] for x in selected)
print("Solver status: ", result.solver.status)

