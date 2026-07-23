# Apply BarPrep Edge 0.2.1-dev

Copy these files into the repository, commit:

```text
Release Edge 0.2.1 QL-800 USB identifier fix
```

Then on the Pi:

```bash
cd ~/barprep-edge-os
git pull --ff-only
sudo bash installer/install.sh
curl http://127.0.0.1:8787/api/status
```

The printer URI should be `usb://0x04f9:0x209b`. Then press **Print test label**.
