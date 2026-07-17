# BarPrep Edge 0.2.0-dev

## Purpose

This release hardens the Brother QL-800 print path against upstream
`brother_ql` API differences found during real Raspberry Pi hardware testing.

## Changes

- Added a dedicated Brother compatibility adapter.
- Uses `brother_ql.backends.helpers.send()` as the preferred print API.
- Retains a guarded `backend_factory()` fallback for older releases.
- Supports discovery results returned as strings, objects, or dictionaries.
- Keeps PyUSB handles and ctypes pointers out of public Edge models.
- Reports the installed `brother-ql` version in health, status, and diagnostics.
- Converts print failures into readable HTTP errors while preserving logs.
- Adds regression tests for discovery and print compatibility.

## Upgrade

```bash
cd ~/barprep-edge-os
git pull
sudo bash installer/install.sh
```

## Verify

```bash
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/api/status
```

Then press **Print test label**.

A successful print appears in Recent activity with the backend mode and
installed brother-ql version.
