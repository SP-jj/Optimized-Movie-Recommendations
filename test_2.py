import pandas as pd
from pyomo.environ import *

# Create a small test dataset
movies = [
    {'tconst': 'm1', 'averageRating': 8.0, 'runtimeMinutes': 120},
    {'tconst': 'm2', 'averageRating': 7.5, 'runtimeMinutes': 90},
    {'tconst': 'm3', 'averageRating': 9.0, 'runtimeMinutes': 150},
    {'tconst': 'm4', 'averageRating': 6.0, 'runtimeMinutes': 60},
]
movies_df = pd.DataFrame(movies)
movie_ids = movies_df['tconst'].tolist()
ratings_dict = {row['tconst']: row['averageRating'] for _, row in movies_df.iterrows()}
runtimes_dict = {row['tconst']: row['runtimeMinutes'] for _, row in movies_df.iterrows()}

# Set total runtime constraint so only some movies can be selected
TOTAL_RUNTIME = 180  # Only two short movies can fit

# Build Pyomo model
model = ConcreteModel()
model.x = Var(movie_ids, domain=Binary)
model.obj = Objective(expr=sum(model.x[m] * ratings_dict[m] for m in movie_ids), sense=maximize)
def runtime_constraint_rule(model):
    return sum(model.x[m] * runtimes_dict[m] for m in movie_ids) <= TOTAL_RUNTIME
model.runtime_constraint = Constraint(rule=runtime_constraint_rule)

# Solve
solver = SolverFactory('gurobi')
result = solver.solve(model)

# Collect selected movies and their ratings
selected = []
for m in movie_ids:
    if model.x[m].value is not None and round(model.x[m].value) == 1:
        selected.append(ratings_dict[m])

manual_sum = sum(selected)
model_sum = model.obj()

print(f"Selected ratings: {selected}")
print(f"Manual sum of ratings: {manual_sum}")
print(f"Model objective value: {model_sum}")
assert abs(manual_sum - model_sum) < 1e-6, "Objective function does not match manual sum!"
print("Test passed: Objective function matches manual sum.")
