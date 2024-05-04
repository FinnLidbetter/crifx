"""Module for writing the report to file."""

import logging
import os

from pylatex import Command, Document, NoEscape, Tabular

from crifx.contest_objects import ProblemSet
from crifx.git_manager import GitManager

REPORT_FILENAME = "crifx-report"


class ReportWriter:
    """Manager class for writing the crifx report."""

    def __init__(self, problem_set: ProblemSet, git_manager: GitManager):
        self.problem_set = problem_set
        self.problem_set.problems.sort(key=lambda x: x.name)
        self.git_manager = git_manager
        self.doc: Document | None = None

    def build_report(self, crifx_dir_path: str) -> Document:
        """Build the report."""
        report_tex_path = os.path.join(crifx_dir_path, REPORT_FILENAME)
        doc = Document(report_tex_path)
        self._set_preamble(doc)
        self._write_body(doc)
        self.doc = doc
        return doc

    def _set_preamble(self, doc: Document):
        """Set the preamble for the tex document."""
        git_short_commit_id = self.git_manager.get_short_commit_id()
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

    def _write_body(self, doc: Document):
        """Write the body for the document."""
        doc.append(NoEscape(r"\maketitle"))
        self._write_summary_table(doc)

    def _write_summary_table(self, doc: Document):
        """Write the summary table for the document."""
        with doc.create(Tabular("|l|c|c|c|c|c|")) as table:
            table.add_hline()
            table.add_row(
                ["Problem", "Independent Solves", "AC", "WA", "TLE", "Test Cases"],
                color="cyan",
            )
            table.add_hline()
            for problem in self.problem_set.problems:
                # colour_independent_count = NoEscape(r"\cellcolor{green}" + str(problem.independent_ac_count()))
                table.add_row(
                    [
                        problem.name,
                        problem.independent_ac_count(),
                        len(problem.ac_submissions),
                        len(problem.wa_submissions),
                        len(problem.tle_submissions),
                        len(problem.test_cases),
                    ]
                )
                table.add_hline()

    def write_tex(self, dirpath):
        """Write the tex output."""
        if self.doc is None:
            raise ValueError(
                "The tex file cannot be written yet. The document has not been built."
            )
        filepath = os.path.join(dirpath, REPORT_FILENAME)
        logging.debug("Writing tex to %s", filepath)
        self.doc.generate_tex(filepath)

    def write_pdf(self, dirpath):
        """Write a pdf file from the tex file."""
        if self.doc is None:
            raise ValueError(
                "The pdf file cannot be written yet. The document has not been built."
            )
        filepath = os.path.join(dirpath, REPORT_FILENAME)
        logging.debug("Writing pdf to %s", filepath)
        self.doc.generate_pdf(filepath, clean=True, clean_tex=False)


def make_crifx_dir(containing_dir_path: str) -> str:
    """Create the crifx directory."""
    crifx_dir_path = os.path.join(containing_dir_path, ".crifx")
    if not os.path.exists(crifx_dir_path):
        os.mkdir(crifx_dir_path)
    return crifx_dir_path
