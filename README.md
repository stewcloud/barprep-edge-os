# BarPrep Edge OS

Reference hardware:

- Raspberry Pi Zero 2 W
- Raspberry Pi OS Lite 64-bit
- Brother QL-800 over USB
- 62 mm continuous label roll

## Current release

**0.1.1-dev — USB Hot-Plug Fix**

This release normalizes Brother discovery results so live PyUSB handles remain
inside the printer driver. The dashboard and JSON API receive only stable,
serializable output-device data.

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

## Current features

- Appliance dashboard
- Persistent identity
- Network and Wi-Fi status
- Automatic Wi-Fi onboarding
- QL-800 discovery and hot-plug
- Local test printing
- Activity history
- Diagnostics export
- Edge API v1 contract
