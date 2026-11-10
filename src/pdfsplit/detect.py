"""Detect whether a page is laid out as two side-by-side columns.

Each page is rendered at low resolution and the vertical strip around the
split line is inspected. If the strip is blank (only background colour) the
columns are separable and the page is split; if any content crosses it (a
centred title, a full-page cover image, a single wide column) the page is
kept whole. Working on the rendered image means this also works for scanned
PDFs, where the text layer may be invisible OCR or missing entirely.
"""

from __future__ import annotations

from collections import Counter

import pypdfium2 as pdfium

# Size in pixels of the page's longer side when rendered for analysis.
RENDER_SIZE = 600
# Half-width of the strip around the split line that must be blank, as a
# fraction of the page width.
GUTTER_MARGIN = 0.01
# A pixel counts as content if it differs from the background by more than this.
INK_THRESHOLD = 48
# Fraction of a column's pixels allowed to be content (scan specks, noise).
NOISE_TOLERANCE = 0.005


def _background(buf: bytes) -> int:
    """Most common gray level in the page, i.e. the paper colour."""
    bins = Counter(v >> 3 for v in buf[::7])
    return (bins.most_common(1)[0][0] << 3) + 4


def is_two_column(page: pdfium.PdfPage, ratio: float = 0.5) -> bool:
    """Return True if nothing on ``page`` crosses the split line at ``ratio``."""
    # Rendering applies /Rotate, so the bitmap matches the page as viewed.
    bitmap = page.render(scale=RENDER_SIZE / max(page.get_size()), grayscale=True)
    w, h, stride = bitmap.width, bitmap.height, bitmap.stride
    buf = bytes(bitmap.buffer)

    background = _background(buf)
    split = round(w * ratio)
    margin = max(2, round(w * GUTTER_MARGIN))
    allowed = int(h * NOISE_TOLERANCE)

    for x in range(max(0, split - margin), min(w, split + margin + 1)):
        ink = sum(
            1 for y in range(h) if abs(buf[y * stride + x] - background) > INK_THRESHOLD
        )
        if ink > allowed:
            return False
    return True
