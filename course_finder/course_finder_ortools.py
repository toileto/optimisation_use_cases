import pandas as pd
from ortools.sat.python import cp_model
from prettytable import PrettyTable


def print_formatted_table(list_of_dict):
    """
    Prints a list of dictionaries in a formatted table with separators.

    Args:
        data: A list of dictionaries containing the data to be printed.

    Returns:
        None
    """

    data = list_of_dict

    # Get column names and widths
    table = PrettyTable()
    table.field_names = list(data[0].keys())

    # Print rows
    for row in data:
        table.add_row(row.values())

    print(table)


# Load course data
data = pd.read_csv("courses.csv")
data = data.sample(frac=1).reset_index(drop=True)
courses = data.to_dict("records")

# Create the model
model = cp_model.CpModel()

# Create decision variables
x = {}
for i in range(len(courses)):
    x[i] = model.NewBoolVar(f"course_{i}")  # 1 if course is taken, 0 otherwise

# Define constraints
model.Add(sum(courses[i]["credit"] * x[i] for i in range(len(courses))) == 180)  # Total credits
model.Add(sum(courses[i]["credit"] * x[i] for i in range(len(courses)) if courses[i]["group"] == "CS") == 120)  # CS group credits
model.Add(sum(courses[i]["credit"] * x[i] for i in range(len(courses)) if courses[i]["group"] != "CS") >= 60) # Other group credits
model.Add(sum(x[i] for i in range(len(courses)) if courses[i]["exam_type"] == "EXAM") == 0)  # No exams allowed

# Define objective function (minimize cost only)
total_cost = sum(courses[i]["cost"] * x[i] for i in range(len(courses)))
model.Minimize(total_cost)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Best scenario found!")
    _cost = 0
    _solution = list()
    for i in range(len(courses)):
        if solver.Value(x[i]) == 1:
            _solution.append(courses[i])
            _cost = _cost + courses[i]['cost']
    if status == cp_model.FEASIBLE:
        print(f"Feasible solution found, with cost = GBP {_cost}")
    elif status == cp_model.OPTIMAL:
        print(f"Feasible solution found, with cost = GBP {_cost}")

    print_formatted_table(_solution)
else:
    print("No solution found.")
