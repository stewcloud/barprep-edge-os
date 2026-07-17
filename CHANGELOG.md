# Changelog

## [0.1.1-dev] — USB Hot-Plug Fix

### Fixed

- Prevented Brother QL discovery from exposing live PyUSB device handles.
- Fixed dashboard and status API crashes when a QL-800 is connected.
- Replaced recursive `dataclasses.asdict()` output serialization with an
  explicit JSON-safe `OutputDevice.to_dict()` contract.

### Added

- Regression tests for the QL-800 discovery result returned by current
  `brother_ql` and PyUSB versions.
- Dashboard and API tests with a connected printer.

## [0.1.0-dev]

### Added

- Raspberry Pi Zero 2 W appliance runtime
- Brother QL-800 USB discovery
- Accurate network detection
- Automatic Wi-Fi setup watchdog
- Wi-Fi setup page
- Test print
- Printer media profile
- Recent activity
- Diagnostics ZIP
- Edge API v1 contract
