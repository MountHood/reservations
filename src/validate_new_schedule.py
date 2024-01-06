"""Module: Validate new schedule"""
from datetime import datetime, timedelta

def validate_new_schedule(provider: dict, new_schedule: list, appt_len_mins: int) -> bool:
    """Validate new schedule against provider's existing schedule.

    This function validates a new schedule against a provider's existing schedule
    to ensure that the new time ranges meet specific criteria, such as being valid ISO dates,
    having an interval of a specified duration from the top of the hour, and not overlapping
    with existing time ranges in the provider's schedule.

    Args:
        provider (dict): The provider's information, including the existing schedule.
        new_schedule (list): List of time ranges to be validated.
        appt_len_mins (int): The duration, in minutes, for each appointment slot.

    Returns:
        bool: True if the new schedule is valid; False otherwise.

    Note:
        Overlapping time ranges are considered invalid. A more sophisticated algorithm
        could be implemented to calculate new time ranges that do not overlap.

    Example:
        >>> provider_info = {'schedule': [{'start': '2024-01-07T08:00:00+00:00',
                                        'end': '2024-01-07T09:00:00+00:00'}]}
        >>> new_schedule = [{'start': '2024-01-07T09:15:00+00:00',
                            'end': '2024-01-07T09:30:00+00:00'}]
        >>> appt_len = 15
        >>> validate_new_schedule(provider_info, new_schedule, appt_len)
        True
    """
    # Check if provider has a valid structure
    if not isinstance(provider, dict) or 'schedule' not in provider:
        return False

    # Validate each time range in the new schedule
    for time_range in new_schedule:
        start_time_str = time_range.get('start')
        end_time_str = time_range.get('end')

        # Check if start and end times are valid ISO dates
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except:
            return False

        # Check if start and end times are an interval
        # of exactly `appt_len_mins` minutes from the top of the hour
        if (start_time.minute % appt_len_mins != 0) or (end_time.minute % appt_len_mins != 0):
            return False

        # Check if end time is at least `appt_len_mins` minutes later than start time
        if end_time < start_time + timedelta(minutes=appt_len_mins):
            return False

        # Check if the new time range overlaps with any existing time range in provider's schedule.
        # This could be handled more gracefully.
        # For example, we could calculate new time ranges that do not overlap.
        for existing_time_range in provider['schedule']:
            existing_start_time = datetime.fromisoformat(existing_time_range['start'])
            existing_end_time = datetime.fromisoformat(existing_time_range['end'])

            if (existing_start_time < end_time and existing_end_time > start_time) or \
               (start_time < existing_end_time and end_time > existing_start_time):
                return False

    return True
