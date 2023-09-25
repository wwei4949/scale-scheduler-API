import unittest
from scale_scheduler_API import optimize_volunteer_assignments
import random

class TestScheduler(unittest.TestCase):
    def generate_volunteer_data(self, num_volunteers=30):
        """Generate random volunteer data for testing."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = [f"{hour}:00-{hour + 1}:00" for hour in range(9, 22)]

        volunteers_data = {}

        for _ in range(num_volunteers):
            volunteer_name = f"Volunteer{_ + 1}"

            is_driver = "Yes" if random.random() < 0.4 else "No"

            selected_times = []
            num_days = random.randint(1, 5)
            available_days = random.sample(days, num_days)
            for day in available_days:
                num_slots = random.randint(1, 3)
                available_slots = random.sample(time_slots, num_slots)

                for i in range(len(available_slots) - 1, 0, -1):
                    curr_slot = int(available_slots[i].split(":")[0])
                    prev_slot = int(available_slots[i - 1].split(":")[0])
                    if curr_slot - prev_slot == 1:
                        available_slots.pop(i)

                for slot in available_slots:
                    selected_times.append(f"{day} {slot}")

            volunteer_limit = random.randint(1, 3)

            volunteers_data[volunteer_name] = {
                "driver": is_driver,
                "availability": selected_times,
                "limit": volunteer_limit
            }

        return volunteers_data

    def setUp(self):
        """Set up sample data for testing."""
        self.sample_volunteers = self.generate_volunteer_data()

    def test_volunteer_limit(self):
        """Test that volunteers are assigned up to their specified limits."""
        result = optimize_volunteer_assignments(self.sample_volunteers)
        for volunteer, details in self.sample_volunteers.items():
            count = sum([volunteer in result[key] for key in result if "Volunteers" in key])
            self.assertTrue(count <= details['limit'])

    def test_volunteer_availability(self):
        """Test that volunteers are assigned only during their available times."""
        result = optimize_volunteer_assignments(self.sample_volunteers)
        for volunteer, details in self.sample_volunteers.items():
            for key, value in result.items():
                if "Volunteers" in key and volunteer in value:
                    scheduled_time = key.split(" at ")[1].split(" ")[0]
                    scheduled_day = key.split(" on ")[1].split(" at ")[0]
                    # Extract the start hour from the scheduled_time
                    start_hour = int(scheduled_time.split(':')[0])

                    # Ensure that the volunteer is available at the scheduled day and time
                    self.assertTrue(f'{scheduled_day} {start_hour}:00-{start_hour + 1}:00' in details['availability'])

    def test_event_scheduling(self):
        """Test that events are scheduled with at least 3 volunteers."""
        result = optimize_volunteer_assignments(self.sample_volunteers)
        for key, value in result.items():
            if "Volunteers" in key:
                self.assertTrue(len(value) >= 3)  # At least 3 volunteers for each event

    def test_event_limit(self):
        """Test that competitions are scheduled on at most 3 days."""
        result = optimize_volunteer_assignments(self.sample_volunteers)
        comp1_days = sum([1 for key in result if "Competition 1 Days" in key])
        comp2_days = sum([1 for key in result if "Competition 2 Days" in key])
        self.assertTrue(comp1_days <= 3)
        self.assertTrue(comp2_days <= 3)

    def test_time_frame_limit(self):
        """Test that each competition has a single timeframe."""
        result = optimize_volunteer_assignments(self.sample_volunteers)
        comp1_timeframe = [result[key] for key in result if "Competition 1 Timeframe" in key]
        comp2_timeframe = [result[key] for key in result if "Competition 2 Timeframe" in key]
        self.assertTrue(len(comp1_timeframe) == 1)
        self.assertTrue(len(comp2_timeframe) == 1)

    def test_no_double_booking(self):
        """Test that a volunteer is not double booked across competitions."""
        result = optimize_volunteer_assignments(self.sample_volunteers)
        for volunteer, details in self.sample_volunteers.items():
            count_per_day = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}
            for key, value in result.items():
                if "Volunteers" in key and volunteer in value:
                    scheduled_day = key.split(" on ")[1].split(" at ")[0]
                    count_per_day[scheduled_day] += 1
            for day, count in count_per_day.items():
                self.assertTrue(count <= 1)

    def test_all_events_scheduled(self):
        """Test that all events are scheduled."""
        result = optimize_volunteer_assignments(self.sample_volunteers)
        comp1_scheduled = sum([1 for key in result if "Competition 1" in key and "Volunteers" in key])
        comp2_scheduled = sum([1 for key in result if "Competition 2" in key and "Volunteers" in key])
        self.assertTrue(comp1_scheduled == 3)
        self.assertTrue(comp2_scheduled == 3)


if __name__ == '__main__':
    unittest.main()
