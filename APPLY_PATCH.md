# Apply BarPrep Edge 0.2.2-dev

Copy these files into the repository and commit:

```text
Release Edge 0.2.2 readable test label
```

Then on the Pi:

```bash
cd ~/barprep-edge-os
git pull --ff-only
sudo bash installer/install.sh
```

The installer adds `fonts-dejavu-core`. Open the dashboard and press
**Print test label** again.
