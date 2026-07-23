# BarPrep Edge 0.3.1 — Core Pairing Alignment

This package aligns the current `barprep-edge-os` project with BarPrep Core v6.1b.

## One pairing contract

- Pairing code: exactly six numeric digits
- Display: `123-456`
- Edge generates no local alphanumeric code
- Edge registers at `POST /api/edge/register`
- Core returns the matching numeric code and a private claim token
- Manager approves the device in Core
- Edge polls `POST /api/edge/pair-status`
- Core delivers the API key once

## Files

- `runtime/barprep_edge/pairing.py` is a complete replacement.
- `patches/web_app_pairing.txt` contains the exact FastAPI route replacement.
- `patches/templates_pairing.txt` describes the required pairing page states.

After applying the changes:

```bash
cd ~/barprep-edge-os
sudo bash installer/install.sh
sudo systemctl restart barprep-edge
```

Delete the existing local pairing state before retesting:

```bash
sudo rm -f /var/lib/barprep-edge/pairing.json
```

The actual data directory may differ if changed in your Edge configuration.
