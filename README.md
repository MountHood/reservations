# reservations
Reservations api

## Setup

1. Create virtual environment: `python3 -m venv venv`
2. Activate virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python src/app.py`

## Endpoints

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "provider_id": 1,
  "schedule": [
    {"start": "2024-01-07T08:00:00+00:00", "end": "2024-01-07T09:00:00+00:00"},
    {"start": "2024-01-06T09:00:00+00:00", "end": "2024-01-06T10:00:00+00:00"}
  ]
}' http://localhost:5000/providers
```

```bash
curl -X GET http://localhost:5000/available_slots
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "client_id": 1,
  "provider_id": 1,
  "slot": "2024-01-05T08:00:00+00:00"
}' http://localhost:5000/reserve_slot
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "client_id": 1,
  "reservation_id": 1
}' http://localhost:5000/confirm_reservation
```
