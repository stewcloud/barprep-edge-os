# Apply BarPrep Edge 0.3.0-dev

Overlay the patch contents onto the current BarPrep Edge repository, commit,
and deploy normally.

Suggested commit:

```text
Release Edge 0.3.0 pairing foundation
```

On the Pi:

```bash
cd ~/barprep-edge-os
git pull --ff-only
sudo bash installer/install.sh
```

Then open:

```text
http://barprep-edge.local:8787/setup/pair
```

The pairing request expects this BarPrep Core endpoint:

```text
POST /api/v1/edge/pair
```

Until the matching Core feature is installed, the pairing page will correctly
report that Core could not be reached or that the endpoint is unavailable.
Existing printer discovery and test printing are unchanged.
