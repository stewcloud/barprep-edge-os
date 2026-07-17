# Apply BarPrep Edge 0.2.0-dev

This release replaces the failing direct `backend_factory()` invocation with a
Brother compatibility adapter.

## Repository

1. Extract the patch.
2. Copy all files into the root of `barprep-edge-os`.
3. Replace matching files.
4. Commit:

```text
Release Edge 0.2.0 Brother compatibility layer
```

5. Push.

## Raspberry Pi

Because the Pi previously contained a local emergency edit, first confirm the
working tree is clean:

```bash
cd ~/barprep-edge-os
git status --short
```

If output appears:

```bash
git stash push -m "Pi local changes before Edge 0.2.0"
```

Then:

```bash
git pull --ff-only
sudo bash installer/install.sh
```

Do not restore the old stash.

## Verification

```bash
curl http://127.0.0.1:8787/healthz
curl http://127.0.0.1:8787/api/status
```

Open `http://barprep-edge.local:8787` and press **Print test label**.
