# Milestone 2 — Hello Edge

## Objective

Prove that the Raspberry Pi boots as a recognizable BarPrep appliance and
serves a useful local management page.

## Delivered

- Persistent device identity
- `barprep-edge` hostname
- mDNS access through `barprep-edge.local`
- Polished status page
- JSON status API
- Health endpoint
- Uptime
- CPU temperature
- Memory usage
- Disk availability
- IP address display
- Runtime, kernel, architecture, and Python versions
- Printer discovery summary
- Systemd startup
- Thirty-second status-page refresh

## Local addresses

```text
http://barprep-edge.local:8787
http://barprep-edge.local:8787/api/status
http://barprep-edge.local:8787/healthz
```

## Hardware acceptance test

1. Install Raspberry Pi OS Lite 64-bit on the Zero 2 W.
2. Configure Wi-Fi temporarily with Raspberry Pi Imager.
3. Clone or copy this repository to the Pi.
4. Run:

```bash
cd barprep-edge-os
sudo bash installer/install.sh
```

5. Reboot:

```bash
sudo reboot
```

6. Open `http://barprep-edge.local:8787`.
7. Confirm system information appears.
8. Unplug and reconnect power.
9. Confirm the same Device ID remains.
10. Confirm the service starts automatically.

Wi-Fi captive onboarding is Milestone 3.
