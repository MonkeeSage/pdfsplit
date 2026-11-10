"""Command-line interface for pdfsplit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pdfsplit import __version__
from pdfsplit.split import default_output_path, split_pdf


def _ratio(value: str) -> float:
    ratio = float(value)
    if not 0 < ratio < 1:
        raise argparse.ArgumentTypeError("must be between 0 and 1 (exclusive)")
    return ratio


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pdfsplit",
        description=(
            "Split PDF pages laid out as two side-by-side columns so each "
            "column becomes its own page."
        ),
    )
    parser.add_argument("input", type=Path, help="input PDF file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output PDF file (default: INPUT with '.pdfsplit' before the extension)",
    )
    parser.add_argument(
        "--split-at",
        type=_ratio,
        default=0.5,
        metavar="RATIO",
        help="fraction of the page width where the columns divide (default: 0.5)",
    )
    parser.add_argument(
        "--no-detect",
        dest="detect",
        action="store_false",
        help="split every page, even ones whose content crosses the split line",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    if not args.input.is_file():
        parser.error(f"input file not found: {args.input}")
    output = args.output or default_output_path(args.input)
    if output.resolve() == args.input.resolve():
        parser.error("output file must differ from the input file")

    try:
        count, kept = split_pdf(args.input, output, args.split_at, args.detect)
    except Exception as exc:  # report PDF parsing/writing errors cleanly
        print(f"pdfsplit: error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {count} pages to {output}")
    if kept:
        pages = ", ".join(str(n) for n in kept)
        print(f"Kept {len(kept)} page(s) whole (not two-column): {pages}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
