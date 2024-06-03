"""Entry point for crifx."""

import argparse
import logging
import os
import sys

from crifx.config_parser import parse_config
from crifx.dir_layout_parsing import find_contest_problems_root
from crifx.git_manager import GitManager
from crifx.problemset_parser import ProblemSetParser
from crifx.report_writer import ReportWriter, make_crifx_dir

CRIFX_ERROR_EXIT_CODE = 1


def _dir_path_argparse_type(path):
    """Check that the provided path is a directory."""
    if os.path.isdir(path):
        return path
    else:
        raise ValueError(f"{path} is not a directory.")


def _make_argument_parser() -> argparse.ArgumentParser:
    """Create an argument parser."""
    parser = argparse.ArgumentParser(
        description="ICPC Contest preparation Reporting and Insights tool For anyone.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "path",
        type=_dir_path_argparse_type,
        nargs="?",
        default=None,
        help="Optional path to a problemset root directory. If not specified then "
        "crifx will test the current directory and up to 5 parent directories "
        "to find the first candidate problemset root directory.",
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
    if args.check:
        raise NotImplementedError("Check-only mode is not supported yet")
    logging.basicConfig(level=log_level, format=log_format)
    logging.debug("Running crifx-cli from %s", os.getcwd())
    if args.path is None:
        problemset_root_path = find_contest_problems_root()
    else:
        problemset_root_path = os.path.abspath(args.path)
    if problemset_root_path is None:
        logging.error(
            "Could not find contest problems root from the current directory: %s",
            os.getcwd(),
        )
        sys.exit(CRIFX_ERROR_EXIT_CODE)
    crifx_dir_path = make_crifx_dir(problemset_root_path)
    config = parse_config(problemset_root_path)
    git_manager = GitManager(problemset_root_path)
    track_review_status = config.track_review_status()
    problemset_parser = ProblemSetParser(
        problemset_root_path,
        git_manager,
        config.alias_groups,
        track_review_status,
    )
    problemset = problemset_parser.parse_problemset()
    writer = ReportWriter(problemset, config, git_manager)
    writer.build_report(crifx_dir_path)
    writer.write_tex(crifx_dir_path)
    writer.write_pdf(problemset_root_path)


if __name__ == "__main__":
    main()
