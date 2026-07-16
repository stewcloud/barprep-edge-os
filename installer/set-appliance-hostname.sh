#!/usr/bin/env bash
set -euo pipefail

TARGET_HOSTNAME="${1:-barprep-edge}"

hostnamectl set-hostname "${TARGET_HOSTNAME}"

if grep -qE '^127\.0\.1\.1\s+' /etc/hosts; then
  sed -i -E "s/^127\.0\.1\.1\s+.*/127.0.1.1\t${TARGET_HOSTNAME}/" /etc/hosts
else
  printf '127.0.1.1\t%s\n' "${TARGET_HOSTNAME}" >> /etc/hosts
fi

systemctl restart avahi-daemon || true
echo "Hostname set to ${TARGET_HOSTNAME}"
