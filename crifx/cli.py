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
        "-o",
        "--output-dir",
        default=None,
        help="Optional directory path to which to write the crifx report pdf. "
        "If omitted, then the report will be written to the problemset "
        "root directory.",
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
    if args.output_dir is None:
        output_dir = problemset_root_path
    else:
        output_dir = os.path.abspath(args.output_dir)
        if not os.path.isdir(output_dir):
            logging.error("Specified output directory '%s' does not exist", output_dir)
            sys.exit(CRIFX_ERROR_EXIT_CODE)
    config = parse_config(problemset_root_path)
    git_manager = GitManager(problemset_root_path)
    track_review_status = config.track_review_status
    problemset_parser = ProblemSetParser(
        problemset_root_path,
        git_manager,
        config.alias_groups,
        track_review_status,
    )
    problemset = problemset_parser.parse_problemset()
    writer = ReportWriter(problemset, config, git_manager)
    crifx_dir_path = make_crifx_dir(output_dir)
    writer.build_report(crifx_dir_path)
    writer.write_tex(crifx_dir_path)
    writer.write_pdf(output_dir)


if __name__ == "__main__":
    main()
