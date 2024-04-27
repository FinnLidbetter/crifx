"""Entry point for crifx."""

import argparse
import logging
import os
import sys

from crifx.dir_layout_parsing import find_contest_problems_root
from crifx.report_writing import (
    REPORT_FILENAME,
    make_crifx_dir,
    smart_open,
    write_report,
)


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
        "--stdout",
        action="store_true",
        help="Write report output to stdout.",
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
    logging.basicConfig(level=log_level)
    crifx_containing_dir = find_contest_problems_root()
    if crifx_containing_dir is None:
        logging.error(
            "Could not find contest problems root from the current directory: %s",
            os.getcwd(),
        )
        sys.exit(23)
    crifx_dir_path = make_crifx_dir(crifx_containing_dir)
    report_path = "-" if args.stdout else os.path.join(crifx_dir_path, REPORT_FILENAME)
    with smart_open(report_path) as report_handle:
        write_report(report_handle)


if __name__ == "__main__":
    main()
