from io import BytesIO

from PIL import Image

from barprep_edge.drivers.brother_ql import BrotherQLDriver


def test_test_label_uses_full_readable_canvas() -> None:
    driver = BrotherQLDriver()
    png = driver.create_test_label(
        "BARPREP EDGE",
        [
            "Printer Test",
            "Device: FB99C2B3",
            "Station: Prep Area",
            "Edge: 0.2.2-dev",
        ],
    )

    image = Image.open(BytesIO(png))

    assert image.size == (696, 420)
    assert image.mode == "RGB"
