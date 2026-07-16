# BarPrep Edge OS Specification

**Revision:** 0.1  
**Status:** Draft  
**Reference release:** Edge OS 0.1.0

## 1. Purpose

BarPrep Edge OS connects BarPrep Core to physical hardware installed at a bar.

The initial supported workflow is cloud printing to a Brother QL-800 over USB.

## 2. Reference architecture

```text
BarPrep Core
    │
    │ Outbound HTTPS
    ▼
BarPrep Edge OS
    │
    │ USB
    ▼
Brother QL-800
```

Edge never requires inbound internet access, port forwarding, or a public IP.

## 3. Product vocabulary

### Label Canvas

The canonical rendered label representation. The initial format is PNG.

### Print Job

A request to print one or more copies of a Label Canvas.

### Station

A physical work area such as Prep, Main Bar, Oyster Bar, or Office.

### Edge Device

A local appliance assigned to a Station.

### Output Device

A printer or other output-capable peripheral attached to an Edge Device.

### Edge Driver

A module that communicates with a class of local hardware.

## 4. Primary user experience

1. Power on Edge.
2. Edge creates `BarPrep-Setup-XXXX` when Wi-Fi is not configured.
3. User connects using a phone.
4. User selects the venue Wi-Fi network.
5. Edge establishes internet access.
6. Edge generates a pairing code.
7. Manager enters the code in BarPrep.
8. Manager assigns the Edge to a Station.
9. Edge detects the QL-800 over USB.
10. User prints a Label Canvas from BarPrep.
11. Edge prints and reports status.

## 5. Reference hardware

- Raspberry Pi Zero 2 W
- Quality microSD card
- 5 V / 2.5 A power supply
- Micro-USB OTG adapter
- Brother QL-800
- 62 mm continuous label roll

## 6. Edge OS 0.1.0 requirements

- Persistent device identity
- First-boot Wi-Fi setup
- Ability to update or reset Wi-Fi
- Secure cloud pairing
- Station assignment
- QL-800 USB discovery
- Local test print
- Label Canvas PNG printing
- Copies and automatic cutting
- Cloud queue polling
- Job acknowledgement
- Heartbeat and device status
- USB reconnect recovery
- Internet reconnect recovery
- Local status page
- Persistent local configuration
- Useful logs and diagnostics

## 7. Print job states

```text
queued
claimed
printing
printed
failed
canceled
```

## 8. Output priority

1. BarPrep Edge
2. Browser print
3. Download or share Label Canvas
4. Optional platform-specific printing
5. Bluetooth as a best-effort future fallback

## 9. Security principles

- Edge initiates all cloud communication.
- Device credentials are unique.
- API requests are signed.
- Pairing codes expire.
- Device secrets are stored with restricted permissions.
- No default SSH exposure in public images.
- Recovery actions require local physical access or authenticated administration.

## 10. Deferred features

- Bluetooth printing
- Additional printer brands
- Network printer drivers
- Scales
- Barcode scanners
- NFC
- Cameras
- Displays
- Proximity detection
- Public OTA update service

## 11. Release target

Edge OS 0.1.0 succeeds when a BarPrep Label Canvas consistently prints on a
QL-800 connected by USB and the job status returns to BarPrep Core.
