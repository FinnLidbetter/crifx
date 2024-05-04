"""Entry point for crifx."""

import argparse
import logging
import os
import sys

from crifx.dir_layout_parsing import find_contest_problems_root
from crifx.git_manager import GitManager
from crifx.problemset_parser import ProblemSetParser
from crifx.report_writer import ReportWriter, generate_pdf, make_crifx_dir, write_report

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
    problemset_root_path = find_contest_problems_root()
    if problemset_root_path is None:
        logging.error(
            "Could not find contest problems root from the current directory: %s",
            os.getcwd(),
        )
        sys.exit(CRIFX_ERROR_EXIT_CODE)
    crifx_dir_path = make_crifx_dir(problemset_root_path)
    git_manager = GitManager(problemset_root_path)
    problemset_parser = ProblemSetParser(problemset_root_path, git_manager)
    problemset = problemset_parser.parse_problemset()
    writer = ReportWriter(problemset, git_manager)
    doc = writer.build_report(crifx_dir_path)
    doc.generate_tex()
    generate_pdf(problemset_root_path, doc)


if __name__ == "__main__":
    main()
