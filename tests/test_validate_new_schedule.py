import unittest

from src.validate_new_schedule import validate_new_schedule

class TestValidateNewSchedule(unittest.TestCase):
    def test_valid(self):
        provider_info = {'schedule': [{'start': '2024-01-07T08:00:00+00:00',
                                        'end': '2024-01-07T09:00:00+00:00'}]}
        new_schedule = [{'start': '2024-01-07T09:15:00+00:00',
                            'end': '2024-01-07T09:30:00+00:00'}]
        appt_len = 15
        result = validate_new_schedule(provider_info, new_schedule, appt_len)
        self.assertTrue(result)

    def test_invalid_end_time(self):
        provider_info = {'schedule': [{'start': '2024-01-07T08:00:00+00:00',
                                        'end': '2024-01-07T09:00:00+00:00'}]}
        new_schedule = [{'start': '2024-01-07T09:15:00+00:00',
                            'end': '2024-01-07T09:20:00+00:00'}]
        appt_len = 15
        result = validate_new_schedule(provider_info, new_schedule, appt_len)
        self.assertFalse(result)

    def test_invalid_interval(self):
        provider_info = {'schedule': [{'start': '2024-01-07T08:00:00+00:00',
                                        'end': '2024-01-07T09:00:00+00:00'}]}
        new_schedule = [{'start': '2024-01-07T09:05:00+00:00',
                            'end': '2024-01-07T09:30:00+00:00'}]
        appt_len = 15
        result = validate_new_schedule(provider_info, new_schedule, appt_len)
        self.assertFalse(result)

    def test_invalid_overlap(self):
        provider_info = {'schedule': [{'start': '2024-01-07T08:00:00+00:00',
                                        'end': '2024-01-07T09:00:00+00:00'}]}
        new_schedule = [{'start': '2024-01-07T07:00:00+00:00',
                            'end': '2024-01-07T09:30:00+00:00'}]
        appt_len = 15
        result = validate_new_schedule(provider_info, new_schedule, appt_len)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
