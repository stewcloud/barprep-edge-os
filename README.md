# BarPrep Edge OS

Reference hardware:

- Raspberry Pi Zero 2 W
- Raspberry Pi OS Lite 64-bit
- Brother QL-800 over USB
- 62 mm continuous label roll

## Current release

**0.2.0-dev — Brother Compatibility Layer**

The Brother driver now isolates upstream library differences behind a stable
Edge adapter. Current releases print through
`brother_ql.backends.helpers.send()`, with a guarded fallback for legacy
versions.

## Install or update

```bash
cd ~/barprep-edge-os
git pull
sudo bash installer/install.sh
```

Open:

```text
http://barprep-edge.local:8787
```

## Verify the printer

```bash
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/api/status
```

Then use **Print test label** from the dashboard.
