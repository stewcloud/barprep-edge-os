# BarPrep Edge OS

BarPrep Edge OS is the appliance software for local BarPrep Edge devices.

The initial reference platform is:

- Raspberry Pi Zero 2 W
- Raspberry Pi OS Lite 64-bit
- Brother QL-800 connected over USB
- 62 mm continuous label roll
- Outbound HTTPS connection to BarPrep Core

## Initial milestone

**Edge OS 0.1.0 — It Prints**

The first milestone proves the complete path:

```text
BarPrep Core
    ↓
Print Job
    ↓
BarPrep Edge OS
    ↓
Brother QL-800 over USB
    ↓
Physical label
```

## Repository layout

```text
barprep-edge-os/
├── .github/workflows/
├── assets/
├── docs/
├── image/
├── installer/
├── runtime/
├── scripts/
├── tests/
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements-dev.txt
```

## Status

Pre-alpha. Do not deploy in production yet.

## Versioning

BarPrep Core and BarPrep Edge OS are versioned separately.

- BarPrep Core baseline: `6.0a`
- BarPrep Edge OS: `0.1.0-dev`
