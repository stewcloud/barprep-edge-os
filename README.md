# BarPrep Edge OS

BarPrep Edge OS is the appliance software for local BarPrep Edge devices.

The initial reference platform is:

- Raspberry Pi Zero 2 W
- Raspberry Pi OS Lite 64-bit
- Brother QL-800 connected over USB
- 62 mm continuous label roll
- Outbound HTTPS connection to BarPrep Core

## Current milestone

**Milestone 2 — Hello Edge**

The runtime now provides:

- Persistent device identity
- Local appliance status page
- `barprep-edge.local` mDNS hostname
- System health and telemetry
- Printer discovery summary
- Automatic startup through systemd

## Local interface

After installation, open:

```text
http://barprep-edge.local:8787
```

APIs:

```text
http://barprep-edge.local:8787/api/status
http://barprep-edge.local:8787/healthz
```

## Install on Raspberry Pi OS Lite

```bash
cd barprep-edge-os
sudo bash installer/install.sh
sudo reboot
```

## Initial product objective

```text
BarPrep Core
    ↓
Print Job
    ↓
BarPrep Edge OS
    ↓
Brother QL-800 over USB
    ↓
Physical label
```

## Status

Pre-alpha. Do not deploy in production yet.

## Versioning

BarPrep Core and BarPrep Edge OS are versioned separately.

- BarPrep Core baseline: `6.0a`
- BarPrep Edge OS: `0.1.0-dev`
