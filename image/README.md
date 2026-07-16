# Image Build

This directory will contain the Raspberry Pi OS image customization.

The reference target is Raspberry Pi Zero 2 W using Raspberry Pi OS Lite
64-bit.

The initial implementation uses Raspberry Pi `pi-gen`. The custom stage is
located at:

```text
image/pi-gen/stage-barprep-edge/
```

A complete automated build workflow will be added after the runtime and Wi-Fi
onboarding flow pass hardware testing.
