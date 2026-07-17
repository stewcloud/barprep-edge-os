from __future__ import annotations

import logging
import time

from .config import settings
from .network import collect_network_status
from .wifi import start_setup_ap

LOGGER = logging.getLogger(__name__)


def main() -> None:
    boot_started = time.monotonic()
    offline_started: float | None = None

    while True:
        status = collect_network_status()
        if status.connected:
            offline_started = None
        elif status.setup_mode:
            offline_started = offline_started or time.monotonic()
        else:
            now = time.monotonic()
            offline_started = offline_started or now
            if (now - boot_started >= settings.wifi_boot_grace_seconds
                    or now - offline_started >= settings.wifi_offline_setup_seconds):
                try:
                    LOGGER.warning("Starting Wi-Fi setup: %s", start_setup_ap())
                except Exception:
                    LOGGER.exception("Unable to start setup access point")
        time.sleep(settings.wifi_watchdog_interval_seconds)


if __name__ == "__main__":
    main()
