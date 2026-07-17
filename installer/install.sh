#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer with sudo."
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

apt-get update
apt-get install -y python3 python3-venv python3-pip network-manager avahi-daemon   libnss-mdns libusb-1.0-0 usbutils iproute2

install -d -m 0755 /opt/barprep-edge
rm -rf /opt/barprep-edge/runtime
cp -R "${REPO_DIR}/runtime" "${REPO_DIR}/pyproject.toml" "${REPO_DIR}/README.md" /opt/barprep-edge/

if [[ ! -d /opt/barprep-edge/.venv ]]; then
  python3 -m venv /opt/barprep-edge/.venv
fi
/opt/barprep-edge/.venv/bin/pip install --upgrade pip
/opt/barprep-edge/.venv/bin/pip install --upgrade /opt/barprep-edge

install -d -m 0700 /var/lib/barprep-edge
install -m 0644 "${REPO_DIR}/installer/barprep-edge.service" /etc/systemd/system/barprep-edge.service
install -m 0644 "${REPO_DIR}/installer/barprep-edge-wifi.service" /etc/systemd/system/barprep-edge-wifi.service
install -m 0644 "${REPO_DIR}/installer/99-barprep-brother.rules" /etc/udev/rules.d/99-barprep-brother.rules
install -m 0755 "${REPO_DIR}/installer/set-appliance-hostname.sh" /usr/local/sbin/barprep-edge-set-hostname

if [[ ! -f /etc/barprep-edge.env ]]; then
  install -m 0600 "${REPO_DIR}/.env.example" /etc/barprep-edge.env
fi

/usr/local/sbin/barprep-edge-set-hostname barprep-edge
udevadm control --reload-rules
udevadm trigger
systemctl daemon-reload
systemctl enable --now NetworkManager avahi-daemon
systemctl enable barprep-edge.service barprep-edge-wifi.service
systemctl restart barprep-edge.service barprep-edge-wifi.service

echo "BarPrep Edge installed."
echo "Dashboard: http://barprep-edge.local:8787"
