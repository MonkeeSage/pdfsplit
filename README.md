# pdfsplit

Split PDF pages laid out as two side-by-side columns (e.g. scanned two-page
spreads) so each column becomes its own page. Page 1 with two columns becomes
page 1 (left column) and page 2 (right column), and so on.

The split is done by cropping, so text, images and OCR layers are preserved
as-is and the output is about the same size as the input.

Pages that aren't two-column (a cover image, a centred title, a single wide
column) are detected and kept unchanged: each page is rendered at low
resolution, and it is only split if the strip around the split line is blank.
Use `--no-detect` to split every page regardless.

## Install

```sh
pipx install .
# or
pip install .
```

## Usage

```sh
pdfsplit book.pdf                 # writes book.pdfsplit.pdf
pdfsplit book.pdf -o out.pdf      # writes out.pdf
pdfsplit book.pdf --split-at 0.52 # columns divide at 52% of the page width
pdfsplit book.pdf --no-detect     # split every page, even single-column ones
```

`python -m pdfsplit` works too.
