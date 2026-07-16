#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer with sudo."
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

apt-get update
apt-get install -y   python3   python3-venv   python3-pip   network-manager   avahi-daemon   libusb-1.0-0

install -d -m 0755 /opt/barprep-edge
cp -R "${REPO_DIR}/runtime" "${REPO_DIR}/pyproject.toml" "${REPO_DIR}/README.md" /opt/barprep-edge/

python3 -m venv /opt/barprep-edge/.venv
/opt/barprep-edge/.venv/bin/pip install --upgrade pip
/opt/barprep-edge/.venv/bin/pip install /opt/barprep-edge

install -d -m 0700 /var/lib/barprep-edge
install -m 0644 "${REPO_DIR}/installer/barprep-edge.service" /etc/systemd/system/barprep-edge.service
install -m 0644 "${REPO_DIR}/installer/99-barprep-brother.rules" /etc/udev/rules.d/99-barprep-brother.rules

if [[ ! -f /etc/barprep-edge.env ]]; then
  install -m 0600 "${REPO_DIR}/.env.example" /etc/barprep-edge.env
fi

udevadm control --reload-rules
udevadm trigger
systemctl daemon-reload
systemctl enable --now barprep-edge.service

echo "BarPrep Edge OS runtime installed."
echo "Open http://barprep-edge.local:8787 after networking is configured."
