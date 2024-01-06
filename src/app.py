"""Reservations Api"""
from datetime import datetime, timedelta, timezone
from flask import Flask, request, jsonify
from validate_new_schedule import validate_new_schedule

app = Flask(__name__)

# In-memory data structures (replace with a database in production).

# providers dictionary. Key: provider_id, Value: provider along w/ their work schedule
providers = {}
# reservations list. Each item is a reservation.
reservations = []

# for prod, would setup request/response models (JSON schema),
# for request validation, documentation generation (OpenAPI/Swagger), and SDK generation.
# API also needs to be secured (e.g., using API key, possibly IP whitelist)

# For prod, would add logging + monitoring

# Configuration: in prod, would use an external config store for this,
# so that if we want to change some config, we don't need to deploy.
# Appointment length, in minutes
APPOINTMENT_LENGTH_MINUTES = 15
# The minimum number of hours required in advance for making a reservation.
RESERVATION_MIN_HOURS_IN_ADVANCE = 24
# Reservation expiration time, in minutes
RESERVATION_EXPIRY_TIME_MINUTES = 30

@app.route('/providers', methods=['POST'])
def submit_availability():
    """Endpoint for providers to submit available times"""
    data = request.json
    provider_id = data.get('provider_id')
    schedule = data.get('schedule')

    if not provider_id or not schedule:
        return jsonify({'error': 'provider_id and schedule are required'}), 400

    # Get provider by id, set default if non-existent
    provider = providers.setdefault(provider_id, {'provider_id': provider_id, 'schedule': []})

    # Validate new schedule
    if not validate_new_schedule(provider, schedule, APPOINTMENT_LENGTH_MINUTES):
        return jsonify({'error': 'Invalid schedule'}), 400

    # Update the provider's schedule
    provider['schedule'].extend(schedule)

    return jsonify(provider)

# Would be good to add filters to this Api,
# e.g., provider_id, start/end times,
# as well as pagination.
@app.route('/available_slots', methods=['GET'])
def get_available_slots():
    """Endpoint for clients to retrieve available appointment slots"""

    # Create a datetime object representing the current date and time
    # in Coordinated Universal Time (UTC).
    # `now` is not affected by the local timezone setting of the server
    # where the code is running. So, if we move servers to a different region
    # of the world, it should not impact functionality.
    now = datetime.now(timezone.utc)
    available_slots = []

    for provider_id, provider in providers.items():
        for time_range in provider['schedule']:
            start_time_str, end_time_str = time_range['start'], time_range['end']
            start_datetime = datetime.fromisoformat(start_time_str)
            end_datetime = datetime.fromisoformat(end_time_str)

            # Generate `APPOINTMENT_LENGTH_MINUTES`-minute time slots within the given time range
            current_time = start_datetime
            while current_time < end_datetime:
                slot_end_time = current_time + timedelta(minutes=APPOINTMENT_LENGTH_MINUTES)

                # Check if the time range is after the next `RESERVATION_MIN_HOURS_IN_ADVANCE` hours
                if current_time > now + timedelta(hours=RESERVATION_MIN_HOURS_IN_ADVANCE):
                    slot = {
                        'provider_id': provider_id,
                        'start': current_time.isoformat(),
                        'end': slot_end_time.isoformat()
                    }

                    # Check if the slot is available (not reserved or confirmed)
                    if all(
                        reservation['provider_id'] != provider_id or (
                            slot['start'] != reservation['slot_start_time']
                            or ('confirmed' not in reservation
                                and now > datetime.fromisoformat(reservation['expiry_time']))
                        )
                        for reservation in reservations
                    ):
                        available_slots.append(slot)

                current_time = slot_end_time

    return jsonify({'available_slots': available_slots})

@app.route('/reserve_slot', methods=['POST'])
def reserve_slot():
    """Endpoint for clients to reserve an available appointment slot"""
    now = datetime.now(timezone.utc)
    data = request.json
    client_id = data.get('client_id')
    provider_id = data.get('provider_id')
    slot_start_time = data.get('slot_start_time')

    if not (client_id and provider_id and slot_start_time):
        return jsonify({'error': 'client_id, provider_id and slot_start_time are required'}), 400

    # Check if the specified provider exists
    if provider_id not in providers:
        return jsonify({'error': 'Provider not found'}), 404

    try:
        slot_start_datetime = datetime.fromisoformat(slot_start_time)
    except:
        return jsonify({'error': 'slot_start_datetime is invalid ISO date string'}), 404

    # Check if the slot start time is within the next `RESERVATION_MIN_HOURS_IN_ADVANCE` hours
    if slot_start_datetime < now + timedelta(hours=RESERVATION_MIN_HOURS_IN_ADVANCE):
        return jsonify({'error': 'Must reserve '
                                 f'{RESERVATION_MIN_HOURS_IN_ADVANCE} '
                                 'hours in advance'}), 404

    # Check if the specified slot is within the provider's schedule
    provider = providers[provider_id]
    if not any(slot_start_datetime >= datetime.fromisoformat(time_range['start'])
               and slot_start_datetime < datetime.fromisoformat(time_range['end'])
               for time_range in provider['schedule']):
        return jsonify({'error': 'Invalid slot for the specified provider'}), 400

    # Check if the specified slot is available (not reserved or confirmed)
    if any(
        reservation['provider_id'] == provider_id
        and reservation['slot_start_time'] == slot_start_time
        and ('confirmed' in reservation
             or now < datetime.fromisoformat(reservation['expiry_time']))
        for reservation in reservations
    ):
        return jsonify({'error': 'Slot already reserved or confirmed'}), 400

    # Create a reservation for the specified slot.
    # This is a critical section. If two concurrent requests come in to reserve the
    # same appointment, the provider could be double booked.
    # For this challenge, this is handled because Flask's development server (Werkzeug)
    # only handles 1 request at a time. For production, rely on database
    # mechanism to handle, e.g., unique constraint.
    reservation_id = len(reservations) + 1
    reservation = {
        'reservation_id': reservation_id,
        'client_id': client_id,
        'provider_id': provider_id,
        'slot_start_time': slot_start_time,
        'slot_end_time': (slot_start_datetime + timedelta(minutes=APPOINTMENT_LENGTH_MINUTES)).isoformat(),
        'expiry_time': (now + timedelta(minutes=RESERVATION_EXPIRY_TIME_MINUTES)).isoformat()
    }
    reservations.append(reservation)

    return jsonify(reservation)

@app.route('/confirm_reservation', methods=['POST'])
def confirm_reservation():
    """Endpoint for clients to confirm their reservation"""
    now = datetime.now(timezone.utc)
    data = request.json
    client_id = data.get('client_id')
    reservation_id = data.get('reservation_id')

    if not client_id or not reservation_id:
        return jsonify({'error': 'client_id and reservation_id are required'}), 400

    for reservation in reservations:
        if reservation['reservation_id'] == reservation_id:
            # Make sure the correct client_id is in request, just in case
            if client_id != reservation['client_id']:
                return jsonify({'error': 'Unexpected client_id'}), 400

            if now < datetime.fromisoformat(reservation['expiry_time']):
                # Remove expiration and set to confirmed
                del reservation['expiry_time']
                reservation['confirmed'] = True
                return jsonify({'message': 'Reservation confirmed'})

            return jsonify({'message': 'Reservation expired, cannot confirm'}), 400

    return jsonify({'message': 'Reservation not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
