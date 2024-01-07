# Basic test that makes two requests in parallel to
# try to reserve the same appointment slot.
# Only one request should succeed.
curl -X POST -H "Content-Type: application/json" -d '{
  "client_id": 1,
  "provider_id": 1,
  "slot_start_time": "2024-01-14T09:45:00+00:00"
}' http://localhost:5000/reserve_slot &
curl -X POST -H "Content-Type: application/json" -d '{
  "client_id": 1,
  "provider_id": 1,
  "slot_start_time": "2024-01-14T09:45:00+00:00"
}' http://localhost:5000/reserve_slot