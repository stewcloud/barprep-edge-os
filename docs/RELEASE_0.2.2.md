# BarPrep Edge 0.2.2-dev

## Readable test-label typography

The original test label used Pillow's tiny built-in bitmap font. This release:

- Installs DejaVu Sans.
- Uses scalable bold TrueType fonts.
- Increases the title to approximately 64 px.
- Uses 30–46 px body text.
- Automatically reduces font size only when a line is too long.
- Uses a 696 × 420 canvas designed for the 62 mm continuous roll.
- Adds stronger spacing, border, and hierarchy.

This affects the local printer self-test. Production BarPrep Label Canvas
rendering remains a separate pipeline.
