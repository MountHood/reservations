# reservations
Reservations api

## Setup

1. Create virtual environment: `python3 -m venv venv`
2. Activate virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python src/app.py`

## Endpoints

**POST /providers**

Endpoint for providers to submit available times.
Start and end times should be in UTC.

Example request:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "provider_id": 1,
  "schedule": [
    {"start": "2024-01-15T08:00:00+00:00", "end": "2024-01-15T09:00:00+00:00"},
    {"start": "2024-01-14T09:00:00+00:00", "end": "2024-01-14T10:00:00+00:00"}
  ]
}' http://localhost:5000/providers
```

Example response:

```json
{
  "provider_id": 1,
  "schedule": [
    {
      "start": "2024-01-15T08:00:00+00:00",
      "end": "2024-01-15T09:00:00+00:00"
    },
    {
      "start": "2024-01-14T09:00:00+00:00",
      "end": "2024-01-14T10:00:00+00:00"
    }
  ]
}
```

**GET /available_slots**

Endpoint for clients to retrieve available appointment slots. Lists all available slots for all providers.

Example request:

```bash
curl -X GET http://localhost:5000/available_slots
```

Example response:

```json
{
  "available_slots": [
    {
      "provider_id": 1,
      "start": "2024-01-15T08:00:00+00:00",
      "end": "2024-01-15T08:15:00+00:00"
    },
    {
      "provider_id": 1,
      "start": "2024-01-15T08:15:00+00:00",
      "end": "2024-01-15T08:30:00+00:00"
    },
    {
      "provider_id": 1,
      "start": "2024-01-15T08:30:00+00:00",
      "end": "2024-01-15T08:45:00+00:00"
    },
    {
      "provider_id": 1,
      "start": "2024-01-15T08:45:00+00:00",
      "end": "2024-01-15T09:00:00+00:00"
    },
    {
      "provider_id": 1,
      "start": "2024-01-14T09:00:00+00:00",
      "end": "2024-01-14T09:15:00+00:00"
    },
    {
      "provider_id": 1,
      "start": "2024-01-14T09:15:00+00:00",
      "end": "2024-01-14T09:30:00+00:00"
    },
    {
      "provider_id": 1,
      "start": "2024-01-14T09:30:00+00:00",
      "end": "2024-01-14T09:45:00+00:00"
    },
    {
      "provider_id": 1,
      "start": "2024-01-14T09:45:00+00:00",
      "end": "2024-01-14T10:00:00+00:00"
    }
  ]
}
```

**POST /reserve_slot**

Endpoint for clients to reserve an available appointment slot.

Example request:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "client_id": 1,
  "provider_id": 1,
  "slot_start_time": "2024-01-14T09:45:00+00:00"
}' http://localhost:5000/reserve_slot
```

Example response:

```json
{
  "client_id": 1,
  "expiry_time": "2024-01-06T21:45:08.436865+00:00",
  "reservation_id": 1,
  "provider_id": 1,
  "slot_start_time": "2024-01-14T09:45:00+00:00",
  "slot_end_time": "2024-01-14T10:00:00+00:00"
}
```

**POST /confirm_reservation**

Endpoint for clients to confirm their reservation.

Example request:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "client_id": 1,
  "reservation_id": 1
}' http://localhost:5000/confirm_reservation
```

Example response:

```json
{
  "message": "Reservation confirmed"
}
```

## Tests

To run unit tests: `python3 -m unittest -v`
