# BarPrep Edge API v1

**Status:** Draft implementation contract  
**Base path:** `/api/v1/edge`  
**Transport:** HTTPS  
**Edge direction:** Edge initiates all internet communication

## Design principles

- BarPrep Core routes work to a Station.
- Edge advertises capabilities and connected output devices.
- Core does not need to know Linux, USB, or driver details.
- Edge never requires inbound internet access.
- Polling is the initial reliable transport.
- A secure WebSocket may later become the primary live transport.
- Polling remains the fallback.

## Device identity

Each Edge has:

- `device_id`: immutable internal identifier
- `device_secret`: unique device credential
- `friendly_name`: manager-controlled name
- `station_id`: physical destination assignment
- `runtime_version`
- `os_version`
- `capabilities`

Example internal ID:

```text
bpe_8d72ab114e3c
```

Example friendly name:

```text
Prep Edge
```

Users normally see the friendly name and Station, not the board model.

## Capabilities

Initial capability identifiers:

```json
[
  "label-printing",
  "usb-printer",
  "wifi",
  "mdns",
  "local-status"
]
```

Reserved future capabilities:

```json
[
  "network-printer",
  "bluetooth-printer",
  "barcode-scanner",
  "scale",
  "nfc",
  "camera",
  "display",
  "speaker",
  "microphone"
]
```

Capabilities indicate what the Edge can do. Output devices describe the actual
connected hardware.

---

## 1. Begin registration

```http
POST /api/v1/edge/register
```

The first public release should require a manager-generated bootstrap token or
another server-authorized claim mechanism. Anonymous unlimited registration is
not acceptable for production.

### Request

```json
{
  "device_id": "bpe_8d72ab114e3c",
  "device_public_name": "BarPrep Edge",
  "runtime_version": "0.1.0",
  "os_version": "0.1.0",
  "capabilities": [
    "label-printing",
    "usb-printer",
    "wifi",
    "mdns",
    "local-status"
  ]
}
```

### Response

```json
{
  "registration_id": "reg_01JZ...",
  "pairing_code": "7QPK",
  "expires_at": "2026-07-16T04:15:00Z",
  "poll_after_seconds": 5
}
```

Pairing codes are four characters for the manager experience, short-lived,
rate-limited, and unique among active registrations.

---

## 2. Check pairing state

```http
GET /api/v1/edge/pairing
```

### Unpaired response

```json
{
  "paired": false,
  "pairing_code": "7QPK",
  "expires_at": "2026-07-16T04:15:00Z"
}
```

### Paired response

```json
{
  "paired": true,
  "organization_id": "org_...",
  "location_id": "loc_...",
  "station_id": "station_prep",
  "station_name": "Prep Area",
  "friendly_name": "Prep Edge",
  "device_token": "returned-once-or-encrypted"
}
```

The pairing completion action is performed by an authenticated manager in
BarPrep Core.

---

## 3. Heartbeat

```http
POST /api/v1/edge/heartbeat
```

Recommended initial interval: 30 seconds.

### Request

```json
{
  "runtime_version": "0.1.0",
  "os_version": "0.1.0",
  "uptime_seconds": 4231,
  "ip_addresses": ["192.168.1.83"],
  "capabilities": [
    "label-printing",
    "usb-printer",
    "wifi",
    "mdns",
    "local-status"
  ],
  "system": {
    "cpu_temperature_c": 51.2,
    "memory_available_bytes": 238706688,
    "disk_free_bytes": 12408733696
  },
  "outputs": [
    {
      "output_id": "usb://0x04f9:0x209b",
      "type": "label-printer",
      "driver": "brother_ql",
      "manufacturer": "Brother",
      "model": "QL-800",
      "connection": "usb",
      "ready": true,
      "media": {
        "label": "62",
        "description": "62 mm continuous"
      },
      "detail": ""
    }
  ],
  "last_job_id": "job_...",
  "last_error": null
}
```

### Response

```json
{
  "accepted": true,
  "server_time": "2026-07-16T04:02:00Z",
  "configuration_revision": 12,
  "recommended_poll_seconds": 2
}
```

---

## 4. Get next print job

```http
GET /api/v1/edge/jobs/next
```

### No job

```http
204 No Content
```

### Job response

```json
{
  "job_id": "job_01JZ...",
  "station_id": "station_prep",
  "output_id": "usb://0x04f9:0x209b",
  "canvas": {
    "canvas_id": "canvas_01JZ...",
    "format": "image/png",
    "sha256": "hex-digest",
    "download_url": "https://barprep.example.com/api/v1/edge/canvases/...",
    "width_mm": 62,
    "height_mm": 32,
    "dpi": 300
  },
  "print": {
    "copies": 1,
    "cut": true
  },
  "created_at": "2026-07-16T04:03:00Z"
}
```

The download URL should be short-lived. Large Label Canvas data should not be
embedded in every queue response.

---

## 5. Claim a job

```http
POST /api/v1/edge/jobs/{job_id}/claim
```

### Request

```json
{
  "output_id": "usb://0x04f9:0x209b"
}
```

### Response

```json
{
  "claimed": true,
  "lease_expires_at": "2026-07-16T04:05:30Z"
}
```

A claim lease prevents two Edge devices assigned to the same Station from
printing the same job.

---

## 6. Report job status

```http
POST /api/v1/edge/jobs/{job_id}/status
```

Valid states:

```text
claimed
downloading
printing
completed
failed
canceled
```

### Request

```json
{
  "status": "completed",
  "attempt": 1,
  "output_id": "usb://0x04f9:0x209b",
  "detail": "",
  "completed_at": "2026-07-16T04:03:12Z"
}
```

Failure example:

```json
{
  "status": "failed",
  "attempt": 2,
  "output_id": "usb://0x04f9:0x209b",
  "error_code": "printer_not_found",
  "detail": "Brother QL-800 is not connected"
}
```

---

## 7. Download Label Canvas

```http
GET /api/v1/edge/canvases/{canvas_id}
```

Response content type:

```text
image/png
```

Required headers:

```text
ETag
Content-Length
X-BarPrep-Canvas-SHA256
```

Edge verifies the hash before printing.

---

## 8. Remote test print request

```http
POST /api/v1/edge/actions/test-print
```

This endpoint is requested by BarPrep Core and delivered through the normal
job mechanism. It should not attempt a direct inbound connection to Edge.

The generated test Label Canvas includes:

- BarPrep Edge
- Friendly Edge name
- Station
- Printer model
- Date and time
- Device ID suffix
- “Printer ready”

---

## 9. Configuration retrieval

```http
GET /api/v1/edge/configuration
```

### Response

```json
{
  "revision": 12,
  "friendly_name": "Prep Edge",
  "station_id": "station_prep",
  "station_name": "Prep Area",
  "poll_interval_seconds": 2,
  "heartbeat_interval_seconds": 30,
  "preferred_output_id": "usb://0x04f9:0x209b"
}
```

Edge applies only newer configuration revisions.

---

## Authentication

After pairing, each request must authenticate the Edge.

The initial implementation may use:

- Device ID
- Timestamp
- Body SHA-256
- HMAC-SHA256 signature

Headers:

```text
X-BarPrep-Device
X-BarPrep-Timestamp
X-BarPrep-Signature
```

Production requirements:

- TLS only
- Replay-window rejection
- Constant-time signature comparison
- Credential rotation support
- Device disable/revoke support
- Rate limiting
- Audit logging

## Transport evolution

### Edge OS 0.1.x

HTTPS polling is the supported transport.

### Future

A secure outbound WebSocket may provide:

- Immediate job delivery
- Live printer-state updates
- Configuration pushes

If the socket is unavailable, Edge falls back to HTTPS polling.
