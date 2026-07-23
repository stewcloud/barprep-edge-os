#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-$HOME/barprep-edge-os}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$REPO/runtime/barprep_edge/web/app.py" ]]; then
  echo "Edge repository not found: $REPO"
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
sudo cp "$REPO/runtime/barprep_edge/pairing.py" "$REPO/runtime/barprep_edge/pairing.py.$STAMP.bak"
sudo cp "$REPO/runtime/barprep_edge/web/app.py" "$REPO/runtime/barprep_edge/web/app.py.$STAMP.bak"
sudo cp "$REPO/runtime/barprep_edge/web/templates.py" "$REPO/runtime/barprep_edge/web/templates.py.$STAMP.bak"

sudo cp "$HERE/files/pairing.py" "$REPO/runtime/barprep_edge/pairing.py"
sudo python3 "$HERE/files/patch_edge.py" "$REPO"

sudo rm -f /var/lib/barprep-edge/pairing.json || true

cd "$REPO"
sudo bash installer/install.sh
sudo systemctl daemon-reload
sudo systemctl restart barprep-edge

echo "Installed BarPrep Edge 0.3.1."
echo "The pairing page should now ask only for the Core URL."
