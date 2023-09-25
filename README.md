# SCALE Volunteer Scheduler API

## Technology Stack

- **Flask**: A micro web framework written in Python, used to handle incoming requests and responses for the API.
- **OR-Tools**: A popular library by Google, offering various optimization algorithms. Used for the main scheduling logic.
- **Python**: The main language for the backend logic and optimization.

## Features

- **Dynamic Scheduling**: The API schedules volunteers based on their availability, ensuring that no two volunteers are double-booked.
- **Optimized Assignments**: Through constraint programming, the API ensures optimized volunteer assignments, ensuring that the most number of volunteers are scheduled while respecting their constraints.
- **Event Limitations**: The API ensures that competitions are scheduled for a maximum of 3 days, ensuring proper distribution of events.

## Usage

1. **Input Format**:
   - The API expects a list of volunteers, with each volunteer having:
     - Name
     - Availability slots
     - Whether they can drive
     - Maximum events they can attend

2. **Endpoint**:
   - `/optimize-schedule`: Accepts a POST request with the above volunteer data in JSON format. Returns an optimized schedule.

3. **Sample Call**:
   ```python
   import requests

   data = {
       "volunteers": [
           {"name": "John Doe", "availability": ["Monday 10:00-11:00", "Wednesday 12:00-13:00"], "canDrive": True, "maxEvents": 2},
           # ... more volunteers
       ]
   }

   response = requests.post("http://<API_URL>/optimize-schedule", json=data)
   print(response.json())
   ```
## Limitations

- **Fixed Time Slots**: The API currently operates with fixed hourly time slots. This might not offer the flexibility needed for events with non-standard durations.
- **Scalability Concerns**: While the API is designed to handle a reasonable number of volunteers efficiently, larger datasets might lead to increased response times.

## Future Work

1. **Enhanced Scalability**: Work on refining the underlying algorithms and logic to handle a larger number of volunteers and events without compromising performance.
2. **Flexible Time Slots**: Update the API to handle a variety of event durations, offering more dynamic scheduling capabilities.
3. **Real-time Updates**: Integrate with a real-time database system to allow for instant updates to scheduled events and volunteer assignments.
