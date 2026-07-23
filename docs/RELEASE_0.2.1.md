# BarPrep Edge 0.2.1-dev

Fixes QL-800 USB identifiers containing malformed serial suffixes. Identifiers
are normalized to `usb://0x04f9:0x209b` during discovery and immediately before
printing.
