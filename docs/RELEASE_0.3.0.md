# BarPrep Edge 0.3.0-dev

## Pairing foundation

This release introduces the Edge side of the BarPrep Core pairing workflow.

### Included

- Local **Pair with BarPrep** page.
- Core URL and one-time pairing-code validation.
- `POST /api/v1/edge/pair` client contract.
- Persistent device token, Edge ID, and station assignment.
- Atomic state writes with owner-only file permissions.
- Pairing status on the Edge dashboard and `/api/status`.
- Local unpair action.
- Pairing events in the activity log.
- Unit tests for persistence, validation, and API response handling.

### Expected BarPrep Core response

```json
{
  "edge_id": "edge-123",
  "device_token": "opaque-secret-token",
  "station": {
    "id": "station-1",
    "name": "Prep Area"
  }
}
```

The device token is never returned through the public Edge status API.

### Next release

Edge 0.3.1 will add authenticated heartbeat reporting after the matching
BarPrep Core endpoint exists. Edge 0.4.0 will add print-job polling,
download, execution, acknowledgement, and retry behavior.
