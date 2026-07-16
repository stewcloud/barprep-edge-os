# BarPrep Core v6.1 — Printing & Edge Module

## Purpose

BarPrep Core must treat Edge as a first-class output system while retaining
browser printing and Label Canvas downloads as universal fallbacks.

## Navigation

```text
Settings
└── Printing & Edge
    ├── Stations
    ├── Edge Devices
    ├── Output Devices
    └── Print Jobs
```

## Stations

Stations represent physical work areas:

- Prep Area
- Main Bar
- Oyster Bar
- Service Bar
- Office

A user selects where the label should physically appear. They do not need to
choose a raw printer model unless troubleshooting or overriding defaults.

Station fields:

- ID
- Name
- Location
- Active/inactive
- Preferred output
- Online output count
- Last activity
- Optional display order

## Edge Devices

Manager-facing card example:

```text
Prep Edge
Prep Area

Online
Brother QL-800 — Ready
Edge OS 0.1.0
Last seen: Now
```

Manager actions:

- Pair a new Edge
- Rename Edge
- Assign or move it to a Station
- Disable/revoke Edge
- Select preferred output
- Send test print
- View diagnostics
- Review recent jobs

Hardware model and IP address belong in diagnostics, not the primary UI.

## Pairing flow

1. Manager opens **Add Edge Device**.
2. Edge displays a four-character code.
3. Manager enters the code.
4. BarPrep displays the pending Edge and detected capabilities.
5. Manager selects a Station and friendly name.
6. Manager confirms.
7. Edge receives assignment and device credentials.
8. BarPrep offers **Print Test Label**.

Pairing codes:

- Four characters
- Exclude ambiguous characters
- Expire after approximately 10–15 minutes
- Rate-limited
- Scoped to an organization
- Invalidated immediately after use

## Output Devices

An Edge may advertise multiple outputs.

Initial output:

```text
Brother QL-800
Type: Label printer
Connection: USB
Driver: Brother QL
Media: 62 mm continuous
```

Future outputs may include:

- Additional label printers
- Receipt printers
- Network printers
- Bluetooth fallback printers

## Label Canvas print interface

### Ready Edge available

Primary action:

```text
Print
Prep Area
```

A compact Station selector is immediately available.

Secondary actions move into **More**:

- Print locally
- Download PNG
- Download PDF
- Share

### No ready Edge

Primary action:

```text
Print Locally
```

BarPrep uses the current Label Canvas preview through browser printing.

### Multiple Stations

Show physical names and status:

```text
Prep Area       Ready
Main Bar        Ready
Oyster Bar      Offline
```

Do not force users to choose a printer driver.

## Station selection priority

Initial recommendation:

1. Current session’s selected Station
2. Last-used Station on this browser/device
3. User default Station
4. Location default Station
5. First ready Station
6. Browser printing fallback

The selected destination must always be visible before the user commits the
print.

## Print Jobs

Manager view fields:

- Created time
- Label description
- User
- Station
- Edge
- Output device
- Copies
- Status
- Attempts
- Failure detail
- Completion time

Actions:

- Retry failed job
- Cancel queued job
- Reprint completed job
- Open Label Canvas
- Change destination before retry

## Online and offline status

Suggested thresholds:

- Online: heartbeat within 75 seconds
- Delayed: heartbeat 75–180 seconds old
- Offline: heartbeat older than 180 seconds
- Printer unavailable: Edge online, output not ready

A temporary internet outage should not immediately mark the appliance as
failed.

## Capabilities

Core stores Edge capabilities and uses them to enable appropriate controls.

Initial capabilities:

- label-printing
- usb-printer
- wifi
- mdns
- local-status

Capabilities are descriptive, not permissions.

## Browser fallback

Browser printing remains available even when Edge is configured.

It is secondary when a ready Edge exists, but never removed.

## BarPrep Core data objects

Required first-class objects:

- `Station`
- `EdgeDevice`
- `OutputDevice`
- `LabelCanvas`
- `PrintJob`
- `DevicePairing`
- `EdgeCapability`

## Initial release boundary

BarPrep Core v6.1 should support:

- Stations
- Pairing
- Edge status
- QL-800 output discovery
- Label Canvas queueing
- Print history
- Retry
- Browser fallback

It does not need:

- Bluetooth support
- Other printer brands
- Scanners or scales
- WebSocket delivery
- OTA update management
