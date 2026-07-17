# Changelog

## [0.2.0-dev] — Brother Compatibility Layer

### Added

- Brother QL compatibility adapter.
- Preferred `brother_ql.backends.helpers.send()` print path.
- Legacy `backend_factory()` fallback.
- Installed `brother-ql` version in health, status, and diagnostics.
- Print compatibility and end-to-end driver regression tests.

### Fixed

- `TypeError: 'dict' object is not callable` when printing through current
  `brother_ql` releases.
- Raw backend failures now produce a readable printer-test HTTP response.

## [0.1.1-dev] — USB Hot-Plug Fix

### Fixed

- Prevented Brother discovery from exposing live PyUSB device handles.
- Fixed dashboard and status API crashes when a QL-800 is connected.
- Replaced recursive serialization with `OutputDevice.to_dict()`.

## [0.1.0-dev]

### Added

- Initial Raspberry Pi appliance runtime and onboarding features.
