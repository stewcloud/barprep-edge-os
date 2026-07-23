# Changelog

## [0.2.1-dev] — QL-800 USB Identifier Fix

### Fixed
- Removed malformed serial suffixes from Brother USB identifiers.
- Prevented `invalid literal for int() with base 16` during QL-800 printing.
- Added defensive normalization before backend send.

## [0.2.0-dev] — Brother Compatibility Layer
- Added current and legacy Brother backend compatibility.
