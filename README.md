# BarPrep Edge OS

Reference hardware:

- Raspberry Pi Zero 2 W
- Raspberry Pi OS Lite 64-bit
- Brother QL-800 over USB
- 62 mm continuous label roll

## Install or update

```bash
cd ~/barprep-edge-os
git pull
sudo bash installer/install.sh
```

Open `http://barprep-edge.local:8787`.

## Automatic Wi-Fi behavior

Edge tries saved networks first. If no connection is available after 90 seconds,
it starts `BarPrep-Setup-XXXX`. After a sustained five-minute outage, setup mode
also becomes available.

## Current features

- Appliance dashboard
- Persistent identity
- Network and Wi-Fi status
- Wi-Fi onboarding
- QL-800 discovery
- Local test printing
- Activity history
- Diagnostics export
- Edge API v1 contract
