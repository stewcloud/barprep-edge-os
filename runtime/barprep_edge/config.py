from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    server_url: str = ""
    edge_name: str = "BarPrep Edge"
    data_dir: Path = Path("/var/lib/barprep-edge")
    bind: str = "0.0.0.0"
    port: int = 8787
    log_level: str = "INFO"

    wifi_interface: str = "wlan0"
    setup_ssid_prefix: str = "BarPrep-Setup"
    setup_password: str = ""
    wifi_boot_grace_seconds: int = 90
    wifi_offline_setup_seconds: int = 300
    wifi_watchdog_interval_seconds: int = 10

    printer_driver: str = "brother_ql"
    printer_model: str = "QL-800"
    printer_label: str = "62"
    printer_label_description: str = "62 mm continuous"
    printer_uri: str = "usb://0x04f9:0x209b"

    poll_interval_seconds: float = 2.0
    heartbeat_interval_seconds: float = 30.0

    model_config = SettingsConfigDict(env_prefix="BARPREP_", env_file=".env", extra="ignore")


settings = Settings()
