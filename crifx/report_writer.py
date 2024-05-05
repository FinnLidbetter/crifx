"""Module for writing the report to file."""

import logging
import os

from pylatex import (
    Command,
    Document,
    Enumerate,
    Itemize,
    NoEscape,
    Section,
    Subsection,
    Tabular,
)
from pylatex.base_classes import Environment
from pylatex.package import Package

from crifx.config_parser import Config
from crifx.contest_objects import Problem, ProblemSet
from crifx.git_manager import GitManager

MARGIN = "2cm"
REPORT_FILENAME = "crifx-report"
INPUT_FILE_LINES_MAX = 10
INPUT_FILE_WIDTH_MAX = 120

LISTING_OPTIONS = [
    NoEscape(r"basicstyle=\footnotesize"),
    NoEscape(r"backgroundcolor=\color{lightgray}"),
    "framexleftmargin=1em",
    "framexrightmargin=1em",
]


class LstListing(Environment):
    """LstListing environment."""

    packages = [Package("listings")]
    escape = False
    content_separator = "\n"


class ReportWriter:
    """Manager class for writing the crifx report."""

    def __init__(
        self, problem_set: ProblemSet, config: Config, git_manager: GitManager
    ):
        self.problem_set = problem_set
        self.crifx_config = config
        self.git_manager = git_manager
        self.doc: Document | None = None

    def build_report(self, crifx_dir_path: str) -> Document:
        """Build the report."""
        report_tex_path = os.path.join(crifx_dir_path, REPORT_FILENAME)
        geometry_options = {
            "tmargin": MARGIN,
            "lmargin": MARGIN,
            "rmargin": MARGIN,
            "bmargin": MARGIN,
        }
        doc = Document(report_tex_path, geometry_options=geometry_options)
        self._set_preamble(doc)
        self._write_body(doc)
        self.doc = doc
        return doc

    def _set_preamble(self, doc: Document):
        """Set the preamble for the tex document."""
        git_short_commit_id = self.git_manager.get_short_commit_id()
        doc.preamble.append(Command("usepackage", "datetime2"))
        doc.preamble.append(Command("usepackage", "listings"))
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
        """Write the body of the document."""
        doc.append(NoEscape(r"\maketitle"))
        self._write_summary_table(doc)
        self._write_how_can_i_help(doc)
        for problem in self.problem_set.problems:
            self._write_problem_details(doc, problem)

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

    def _write_how_can_i_help(self, doc: Document):
        """Write the 'How can I help?' section."""
        with doc.create(Section("How can I help?")):
            doc.append(
                "TODO: replace these with more specific suggestions based on "
                "what is present and what is still required."
            )
            with doc.create(Enumerate()) as enum_env:
                enum_env.add_item("Write AC submissions")
                enum_env.add_item("Add test data")
                enum_env.add_item("Add WA submissions")
                enum_env.add_item("Add TLE submissions")
                enum_env.add_item("Add input validators")
                enum_env.add_item("Review problem statements")
                enum_env.add_item("Review test data")
                enum_env.add_item("Review input validators")

    def _write_problem_details(self, doc: Document, problem: Problem):
        """Write the details for a problem."""
        doc.append(Command(r"newpage"))
        with doc.create(Section(problem.name)):
            with doc.create(Subsection("Problemtools verifyproblem output")):
                if problem.review_status.run_problemtools:
                    doc.append("null")
                else:
                    doc.append(
                        "Including problemtools verifyproblem output is disabled "
                        "for this problem. It can be enabled in the "
                        "crifx-problem-status.toml file for this problem."
                    )
            with doc.create(Subsection("Test Cases")):
                doc.append(
                    "Test case descriptions are rendered below if they exist. "
                    f"Otherwise, the first {INPUT_FILE_LINES_MAX} lines of input "
                    f"are rendered if they each have at most {INPUT_FILE_WIDTH_MAX} "
                    "characters."
                )
                with doc.create(Itemize()) as itemize:
                    for test_case in problem.test_cases:
                        itemize.add_item(test_case.name)
                        if test_case.has_description:
                            desc_filepath = os.path.join(
                                test_case.dir_path, f"{test_case.name}.desc"
                            )
                            itemize.append(
                                Command(
                                    "lstinputlisting",
                                    NoEscape(desc_filepath),
                                    options=LISTING_OPTIONS,
                                )
                            )
                        else:
                            if all(
                                len(line) <= INPUT_FILE_WIDTH_MAX
                                for line in test_case.input_lines[:INPUT_FILE_LINES_MAX]
                            ):
                                truncated_input = "".join(test_case.input_lines[:10])
                                with doc.create(LstListing(options=LISTING_OPTIONS)):
                                    doc.append(
                                        truncated_input,
                                    )
                                lines_remaining = (
                                    len(test_case.input_lines) - INPUT_FILE_LINES_MAX
                                )
                                if lines_remaining > 0:
                                    doc.append(
                                        f"The remaining {lines_remaining} lines have not been rendered "
                                        f"for brevity."
                                    )
                            else:
                                doc.append(
                                    "Input file lines are too long to render here."
                                )

    def write_tex(self, dirpath: str):
        """Write the tex output."""
        if self.doc is None:
            raise ValueError(
                "The tex file cannot be written yet. The document has not been built."
            )
        filepath = os.path.join(dirpath, REPORT_FILENAME)
        logging.debug("Writing tex to %s", filepath)
        self.doc.generate_tex(filepath)

    def write_pdf(self, dirpath: str):
        """Write a pdf file from the tex file."""
        if self.doc is None:
            raise ValueError(
                "The pdf file cannot be written yet. The document has not been built."
            )
        filepath = os.path.join(dirpath, REPORT_FILENAME)
        logging.debug("Writing pdf to %s", filepath)
        self.doc.generate_pdf(filepath, clean=True, clean_tex=True)


def make_crifx_dir(containing_dir_path: str) -> str:
    """Create the crifx directory."""
    crifx_dir_path = os.path.join(containing_dir_path, ".crifx")
    if not os.path.exists(crifx_dir_path):
        os.mkdir(crifx_dir_path)
    return crifx_dir_path
