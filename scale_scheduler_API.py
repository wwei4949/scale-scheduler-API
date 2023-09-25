"""
SCALE Volunteer Scheduler API
=====================================

Description:
------------
This API leverages Google's OR-Tools to optimize the assignments based on constraints such as volunteer availability,
preferences, and event requirements. The primary endpoint '/optimize-schedule' takes in a list of volunteers and their
availability and returns an optimized schedule for the events.

Usage:
------
Make a POST request to the '/optimize-schedule' endpoint with a list of volunteers and their details.
The API will return an optimized schedule for the volunteers.

Author: Wenjie Wei
Date: 2021-10-25
Version: 1.0.0
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from ortools.sat.python import cp_model

app = Flask(__name__)
CORS(app)

def optimize_volunteer_assignments(volunteers):
    """Optimizes volunteer assignments for SCALE events."""
    model = cp_model.CpModel()

    # Define days and time slots
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = list(range(9, 16))

    # Decision variable: Is volunteer v scheduled on day d, time t for competition c?
    x = {}
    for v in volunteers:
        for d in days:
            for t in time_slots:
                for c in range(2):  # Two competitions
                    x[v, d, t, c] = model.NewBoolVar(f'x_{v}_{d}_{t}_{c}')

    # Decision variable: Is the event for competition c scheduled on day d, time t?
    y = {}
    for d in days:
        for t in time_slots:
            for c in range(2):
                y[d, t, c] = model.NewBoolVar(f'y_{d}_{t}_{c}')

    # Decision variable for the selected time slot for each competition
    z = {}
    for t in time_slots:
        for c in range(2):
            z[t, c] = model.NewBoolVar(f'z_{t}_{c}')

    # Only one time slot should be selected for each competition
    for c in range(2):
        model.Add(sum(z[t, c] for t in time_slots) == 1)

    # If a time slot is selected, the events for that competition must be scheduled in that time slot
    for t in time_slots:
        for d in days:
            for c in range(2):
                model.Add(y[d, t, c] <= z[t, c])

    # Constraints ensuring only 3 days are chosen for each competition
    for c in range(2):
        model.Add(sum(y[d, t, c] for d in days for t in time_slots) == 3)

    # Constraints ensuring not more than one event for the same competition is on the same day
    for d in days:
        for c in range(2):
            model.Add(sum(y[d, t, c] for t in time_slots) <= 1)

    # Volunteers' availability and no double-booking
    for v in volunteers:
        for d in days:
            for t in time_slots:
                for c in range(2):
                    if f'{d} {t}:00-{t + 1}:00' not in volunteers[v]['availability']:
                        model.Add(x[v, d, t, c] == 0)
                    else:
                        # Prevent double-booking across competitions
                        model.Add(sum(x[v, d, t, c2] for c2 in range(2)) <= 1)

    # At least 3 volunteers for each event
    for d in days:
        for t in time_slots:
            for c in range(2):
                for v in volunteers:
                    model.Add(x[v, d, t, c] <= y[d, t, c])

    # Volunteers' limit constraints
    for v in volunteers:
        model.Add(sum(x[v, d, t, c] for d in days for t in time_slots for c in range(2)) <= volunteers[v]['limit'])

    # Validate that if a timeframe is chosen for a competition, there are available volunteers
    for t in time_slots:
        for c in range(2):
            model.Add(sum(x[v, d, t, c] for v in volunteers for d in days) >= z[t, c])

    # Objective: Maximize the number of scheduled volunteers
    model.Maximize(sum(x[v, d, t, c] for v in volunteers for d in days for t in time_slots for c in range(2)))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        solution = {}
        for t in time_slots:
            for c in range(2):
                if solver.Value(z[t, c]) == 1:
                    solution[f"Competition {c + 1} Timeframe"] = f'{t}:00-{t + 1}:00'
        for d in days:
            for c in range(2):
                if sum(solver.Value(y[d, t, c]) for t in time_slots) > 0:
                    if f"Competition {c + 1} Days" in solution:
                        solution[f"Competition {c + 1} Days"].append(d)
                    else:
                        solution[f"Competition {c + 1} Days"] = [d]

                    # Add the volunteers for each scheduled event
                    for t in time_slots:
                        if solver.Value(y[d, t, c]) == 1:
                            scheduled_volunteers = [
                                v for v in volunteers if solver.Value(x[v, d, t, c]) == 1
                            ]
                            if scheduled_volunteers:
                                key = f"Competition {c + 1} Volunteers on {d} {t}:00-{t + 1}:00"
                                solution[key] = scheduled_volunteers
        return solution
    else:
        return 'No optimal solution found'

@app.route('/optimize-schedule', methods=['POST'])
def optimize_schedule():
    volunteer_list = request.json['volunteers']
    # Convert the list of volunteers to a dictionary
    volunteer_data = {v['name']: {
        'availability': v['availability'],
        'driver': v['canDrive'],
        'limit': v['maxEvents']
    } for v in volunteer_list}
    result = optimize_volunteer_assignments(volunteer_data)
    print("response: ", result)

    response = jsonify(result)
    return response, 200

if __name__ == '__main__':
    app.run(debug=True)