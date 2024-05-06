"""Module for writing the report to file."""

import logging
import os

from pylatex import (
    Command,
    Document,
    Enumerate,
    Itemize,
    MultiColumn,
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
INPUT_FILE_WIDTH_MAX = 90

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
        self.doc = Document(report_tex_path, geometry_options=geometry_options)
        self._set_preamble()
        self._write_body()
        return self.doc

    def _set_preamble(self):
        """Set the preamble for the tex document."""
        git_short_commit_id = self.git_manager.get_short_commit_id()
        self.doc.preamble.append(Command("usepackage", "datetime2"))
        self.doc.preamble.append(Command("usepackage", "listings"))
        self.doc.preamble.append(
            Command("title", "CRIFX Contest Preparation Status Report")
        )
        self.doc.preamble.append(
            Command(
                "date",
                NoEscape(
                    f"Compiled \\today~at \\DTMcurrenttime\\DTMcurrentzone~"
                    f"for commit {git_short_commit_id}"
                ),
            )
        )

    def _write_body(self):
        """Write the body of the document."""
        self.doc.append(NoEscape(r"\maketitle"))
        self._write_summary_table()
        self._write_how_can_i_help()
        for problem in self.problem_set.problems:
            self._write_problem_details(problem)

    def _write_summary_table(self):
        """Write the summary table for the document."""
        language_group_configs = self.crifx_config.language_group_configs
        language_groups = [
            group_config.language_group for group_config in language_group_configs
        ]
        requirements = self.crifx_config.review_requirements
        show_statement_reviews = requirements.statement_reviewers > 0
        show_validator_reviews = requirements.validator_reviewers > 0
        show_data_reviews = requirements.data_reviewers > 0
        review_columns = (
            int(show_statement_reviews)
            + int(show_validator_reviews)
            + int(show_data_reviews)
        )
        num_columns = 7 + len(language_group_configs) + review_columns
        column_spec = "|l|" + "c|" * (num_columns - 1)
        with self.doc.create(Tabular(column_spec)) as table:
            table.add_hline()
            header_group_row = [
                # Problem
                "",
                # Independent, Groups, language_groups, Sum
                MultiColumn(
                    3 + len(language_group_configs),
                    align="c",
                    data=NoEscape(r"{\tiny Solutions}"),
                ),
                # WA, TLE
                MultiColumn(2, align="|c|", data=NoEscape(r"{\tiny Non-solutions}")),
                # Test cases
                "",
            ]
            if review_columns > 0:
                header_group_row.append(
                    MultiColumn(
                        review_columns,
                        align="c",
                        data=NoEscape(r"{\tiny Manual Reviews}"),
                    )
                )
            table.add_row(header_group_row, color="cyan")
            table.add_hline()
            header_row = [
                NoEscape(r"{\tiny Problem}"),
                NoEscape(r"{\tiny Independent}"),
                NoEscape(r"{\tiny Groups}"),
            ]
            for language_group_config in language_group_configs:
                header_row.append(
                    NoEscape(r"{\tiny " + language_group_config.identifier + r"}")
                )
            header_row.extend(
                [
                    NoEscape(r"{\tiny Sum}"),
                    NoEscape(r"{\tiny WA}"),
                    NoEscape(r"{\tiny TLE}"),
                    NoEscape(r"{\tiny Test Files}"),
                ]
            )
            if show_statement_reviews:
                header_row.append(NoEscape(r"{\tiny Statement}"))
            if show_validator_reviews:
                header_row.append(NoEscape(r"{\tiny Validator(s)}"))
            if show_data_reviews:
                header_row.append(NoEscape(r"{\tiny Data}"))
            table.add_row(
                header_row,
                color="cyan",
            )
            table.add_hline()
            for problem in self.problem_set.problems:
                row = [
                    problem.name,
                    self._coloured_cell(
                        problem.independent_ac_count(), requirements.independent_ac
                    ),
                    self._coloured_cell(
                        problem.language_groups_ac_covered(language_groups),
                        requirements.language_groups_ac,
                    ),
                ]
                for language_group_config in language_group_configs:
                    language_group = language_group_config.language_group
                    count = 0
                    for ac_submission in problem.ac_submissions:
                        if language_group.has_language(ac_submission.language):
                            count += 1
                    row.append(
                        self._coloured_cell(
                            count, language_group_config.required_ac_count
                        )
                    )
                row.extend(
                    [
                        len(problem.ac_submissions),
                        len(problem.wa_submissions),
                        len(problem.tle_submissions),
                        len(problem.test_cases),
                    ]
                )
                if show_statement_reviews:
                    row.append(
                        self._coloured_cell(
                            len(problem.review_status.statement_reviewed_by),
                            requirements.statement_reviewers,
                        )
                    )
                if show_validator_reviews:
                    row.append(
                        self._coloured_cell(
                            len(problem.review_status.validators_reviewed_by),
                            requirements.validator_reviewers,
                        )
                    )
                if show_data_reviews:
                    row.append(
                        self._coloured_cell(
                            len(problem.review_status.data_reviewed_by),
                            requirements.data_reviewers,
                        )
                    )
                table.add_row(row)
                table.add_hline()

    @staticmethod
    def _coloured_cell(value, requirement):
        if requirement == 0:
            return value
        if value < requirement:
            return NoEscape(r"\cellcolor{red}" + f"{value}/{requirement}")
        else:
            return NoEscape(r"\cellcolor{green}" + f"{value}/{requirement}")

    def _write_how_can_i_help(self):
        """Write the 'How can I help?' section."""
        with self.doc.create(Section("How can I help?")):
            self.doc.append(
                "TODO: replace these with more specific suggestions based on "
                "what is present and what is still required."
            )
            with self.doc.create(Enumerate()) as enum_env:
                enum_env.add_item("Write AC submissions")
                enum_env.add_item("Add test data")
                enum_env.add_item("Add WA submissions")
                enum_env.add_item("Add TLE submissions")
                enum_env.add_item("Add input validators")
                enum_env.add_item("Review problem statements")
                enum_env.add_item("Review test data")
                enum_env.add_item("Review input validators")

    def _write_problem_details(self, problem: Problem):
        """Write the details for a problem."""
        assert self.doc is not None
        self.doc.append(Command(r"newpage"))
        with self.doc.create(Section(problem.name)):
            with self.doc.create(Subsection("Problemtools verifyproblem output")):
                if problem.review_status.run_problemtools:
                    self.doc.append("null")
                else:
                    self.doc.append(
                        "Including problemtools verifyproblem output is disabled "
                        "for this problem. It can be enabled in the "
                        "crifx-problem-status.toml file for this problem."
                    )
            with self.doc.create(Subsection("Test Cases")):
                self.doc.append(
                    "Test case descriptions are rendered below if they exist. "
                    f"Otherwise, the first {INPUT_FILE_LINES_MAX} lines of input "
                    f"are rendered if they each have at most {INPUT_FILE_WIDTH_MAX} "
                    "characters."
                )
                with self.doc.create(Itemize()) as itemize:
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
                                with self.doc.create(
                                    LstListing(options=LISTING_OPTIONS)
                                ):
                                    self.doc.append(
                                        truncated_input,
                                    )
                                lines_remaining = (
                                    len(test_case.input_lines) - INPUT_FILE_LINES_MAX
                                )
                                if lines_remaining > 0:
                                    self.doc.append(
                                        f"The remaining {lines_remaining} lines have not been rendered "
                                        f"for brevity."
                                    )
                            else:
                                self.doc.append(
                                    "\nInput file lines are too long to render here."
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
