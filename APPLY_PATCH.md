# Apply BarPrep Edge 0.1.1-dev

This release fixes the QL-800 hot-plug dashboard crash.

## Repository update

1. Extract this ZIP.
2. Copy all contents into the root of your `barprep-edge-os` repository.
3. Replace matching files.
4. Commit with:

```text
Release Edge 0.1.1 USB hot-plug fix
```

5. Push to GitHub.

## Update the Raspberry Pi

```bash
cd ~/barprep-edge-os
git pull
sudo bash installer/install.sh
```

Then verify:

```bash
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/api/status
```

Open:

```text
http://barprep-edge.local:8787
```

The dashboard should load with the QL-800 connected. Then use **Print test
label** to validate the complete local print path.
