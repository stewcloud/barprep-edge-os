# Milestone 4 — Appliance Features

Included:

- Accurate active-interface network detection
- Appliance state badge
- Automatic setup hotspot after 90 seconds without Wi-Fi
- Setup mode after five minutes of sustained disconnection
- Wi-Fi scan and change page
- Brother QL-800 test print
- Printer media profile display
- Recent activity log
- Downloadable diagnostics bundle
- Wi-Fi watchdog systemd service

Update the Pi:

```bash
cd ~/barprep-edge-os
git pull
sudo bash installer/install.sh
```

Then refresh `http://barprep-edge.local:8787`.

Cloud pairing remains inactive until BarPrep Core v6.1 implements the API.
