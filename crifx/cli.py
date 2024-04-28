"""Entry point for crifx."""

import argparse
import logging
import os
import sys

from crifx.dir_layout_parsing import find_contest_problems_root
from crifx.report_writing import generate_pdf, make_crifx_dir, write_report

CRIFX_ERROR_EXIT_CODE = 23


def _make_argument_parser() -> argparse.ArgumentParser:
    """Create an argument parser."""
    parser = argparse.ArgumentParser(
        description="ICPC Contest preparation Reporting and Insights tool For anyone.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Set verbose logging mode.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if the crifx report is up-to-date, without modifying any files.",
    )
    return parser


def main():
    """Entry point for crifx."""
    args = _make_argument_parser().parse_args()
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    log_format = (
        "[%(asctime)s][%(levelname)s][%(name)s] %(message)s\t[%(filename)s:%(lineno)d]"
    )
    logging.basicConfig(level=log_level, format=log_format)
    logging.debug("Running crifx-cli from %s", os.getcwd())
    crifx_containing_dir = find_contest_problems_root()
    if crifx_containing_dir is None:
        logging.error(
            "Could not find contest problems root from the current directory: %s",
            os.getcwd(),
        )
        sys.exit(CRIFX_ERROR_EXIT_CODE)
    crifx_dir_path = make_crifx_dir(crifx_containing_dir)
    doc = write_report(crifx_dir_path)
    generate_pdf(crifx_containing_dir, doc)


if __name__ == "__main__":
    main()
