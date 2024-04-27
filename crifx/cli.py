"""Entry point for crifx."""

import argparse

from crifx.report_writer import write_report


def _make_argument_parser() -> argparse.ArgumentParser:
    """Create an argument parser."""
    parser = argparse.ArgumentParser(
        description="ICPC Contest preparation Reporting and Insights tool For anyone.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output-file-path",
        type=argparse.FileType("w", encoding="UTF-8"),
        default="-",
        help="File to which the reporting output is written.",
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
    write_report(args.output_file_path)


if __name__ == "__main__":
    main()
