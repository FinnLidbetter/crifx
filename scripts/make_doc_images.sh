#!/bin/bash

set -e

test -e pyproject.toml

magick -quality 200 -density 200 -scene 1 \
  examples/example_problemset/crifx-report.pdf \
  doc/images/example-report-page-%d.png

for png_file in doc/images/example-report-page-*.png
do
    magick "${png_file}" -background white -alpha remove -alpha off "${png_file}"
done
