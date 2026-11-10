"""Core logic for splitting side-by-side PDF pages."""

from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

from pdfsplit.detect import is_two_column


def default_output_path(input_path: Path) -> Path:
    """Return ``name.pdfsplit.ext`` next to the input file."""
    return input_path.with_name(f"{input_path.stem}.pdfsplit{input_path.suffix}")


def _halves(box: RectangleObject, rotation: int, ratio: float) -> tuple[list, list]:
    """Return (first, second) half rectangles of ``box`` as displayed.

    The split is a vertical line on the page as viewed, so for pages rotated
    by 90/270 degrees it is a horizontal line in PDF user space.
    """
    left, bottom, right, top = (float(v) for v in box)
    rotation %= 360
    if rotation in (90, 270):
        split = bottom + (top - bottom) * ratio
        lower = [left, bottom, right, split]
        upper = [left, split, right, top]
        # Rotated 90 clockwise, user-space bottom ends up on the visual left.
        return (lower, upper) if rotation == 90 else (upper, lower)
    split = left + (right - left) * ratio
    left_half = [left, bottom, split, top]
    right_half = [split, bottom, right, top]
    return (right_half, left_half) if rotation == 180 else (left_half, right_half)


def _set_box(page, rect: list) -> None:
    box = RectangleObject(rect)
    page.mediabox = box
    page.cropbox = box
    for name in ("/TrimBox", "/BleedBox", "/ArtBox"):
        if name in page:
            del page[name]


def split_pdf(
    input_path: Path, output_path: Path, ratio: float = 0.5, detect: bool = True
) -> tuple[int, list[int]]:
    """Split pages of ``input_path`` into two pages at ``ratio`` of their width.

    With ``detect``, pages whose content crosses the split line are copied
    unchanged instead of being split.

    Returns the number of pages written and the 1-based numbers of the input
    pages that were kept whole.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    rendered = pdfium.PdfDocument(input_path) if detect else None
    kept = []

    for number, page in enumerate(reader.pages, start=1):
        if rendered is not None and not is_two_column(rendered[number - 1], ratio):
            writer.add_page(page)
            kept.append(number)
            continue
        first, second = _halves(page.cropbox, page.rotation, ratio)
        # Both halves share the same content stream and resources; only the
        # visible box differs, so the output stays roughly the input's size.
        _set_box(writer.add_page(page), first)
        right = writer.add_page(page)
        _set_box(right, second)

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    if rendered is not None:
        rendered.close()

    with open(output_path, "wb") as fh:
        writer.write(fh)
    return len(writer.pages), kept
