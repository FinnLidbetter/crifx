"""Module for writing the report to file."""

import logging
import os

from pygit2 import Repository, discover_repository
from pylatex import Command, Document, NoEscape

REPORT_FILENAME = "crifx-report"


def _get_git_commit_id(crifx_dir_path: str) -> str:
    """Get the current git commit id."""
    repository_path = discover_repository(crifx_dir_path)
    if repository_path is None:
        return "Unknown"
    repo = Repository(repository_path)
    return repo.head.target


def _get_git_short_commit_id(crifx_dir_path: str) -> str:
    """Get the first 8 characters of the current git commit id."""
    commit_id_str = str(_get_git_commit_id(crifx_dir_path))
    return commit_id_str[:8]


def make_crifx_dir(containing_dir_path: str) -> str:
    """Create the crifx directory."""
    crifx_dir_path = os.path.join(containing_dir_path, ".crifx")
    if not os.path.exists(crifx_dir_path):
        os.mkdir(crifx_dir_path)
    return crifx_dir_path


def write_report(crifx_dir_path: str) -> Document:
    """Write the crifx report tex file."""
    git_short_commit_id = _get_git_short_commit_id(crifx_dir_path)
    report_tex_path = os.path.join(crifx_dir_path, REPORT_FILENAME)
    doc = Document(report_tex_path)
    doc.preamble.append(Command("usepackage", "datetime2"))
    doc.preamble.append(Command("title", "CRIFX Contest Preparation Status Report"))
    doc.preamble.append(
        Command(
            "date",
            NoEscape(
                f"Compiled \\today~at \\DTMcurrenttime\\DTMcurrentzone~"
                f"for commit {git_short_commit_id}"
            ),
        )
    )
    doc.append(NoEscape(r"\maketitle"))
    logging.debug("Writing tex file to %s.tex", report_tex_path)
    doc.generate_tex()
    return doc


def generate_pdf(pdf_dir_path, doc: Document):
    """Generate the crifx pdf report."""
    report_pdf_path = os.path.join(pdf_dir_path, REPORT_FILENAME)
    logging.debug("Generating pdf at %s.pdf", report_pdf_path)
    doc.generate_pdf(report_pdf_path, clean=True, clean_tex=True)
