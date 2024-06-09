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
    Subsubsection,
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
            Command(
                "usepackage",
                ("hyperref",),
                ("colorlinks=true", "urlcolor=blue", "linkcolor=blue"),
            )
        )
        self.doc.preamble.append(Command("usepackage", "fancyhdr"))
        self.doc.preamble.append(Command("pagestyle", ("fancy",)))
        self.doc.preamble.append(Command("label", "TOP"))
        self.doc.preamble.append(
            Command(
                "fancyhead",
                (Command("hyperref", ("Back to Top",), ("TOP",)),),
                ("HR",),
            )
        )
        self.doc.preamble.append(
            Command("definecolor", ("insufficientred", "RGB", "255,100,100"))
        )
        self.doc.preamble.append(
            Command("definecolor", ("sufficientgreen", "RGB", "0,210,0"))
        )
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
        self._write_manual_reviews_table()
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
        num_columns = 7 + len(language_group_configs)
        column_spec = "|l|" + "c|" * (num_columns - 1)
        with self.doc.create(Section("Submissions summary", numbering=False)):
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
                    MultiColumn(
                        2, align="|c|", data=NoEscape(r"{\tiny Non-solutions}")
                    ),
                    # Test cases
                    "",
                ]
                table.add_row(header_group_row, color="cyan")
                table.add_hline()
                header_row = [
                    NoEscape(r"{\tiny Problem}"),
                    NoEscape(r"{\tiny Independent}"),
                    NoEscape(r"{\tiny Lang. Groups}"),
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
                table.add_row(
                    header_row,
                    color="cyan",
                )
                table.add_hline()
                for problem in self.problem_set.problems:
                    row = [
                        Command("hyperref", (problem.name,), (f"sec:{problem.name}",)),
                        self._coloured_cell(
                            problem.independent_ac_count(), requirements.independent_ac
                        ),
                        self._coloured_cell(
                            len(problem.language_groups_ac_covered(language_groups)),
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
                    table.add_row(row)
                    table.add_hline()

    def _write_manual_reviews_table(self):
        """Write a table with a summary tracking manual reviews."""
        requirements = self.crifx_config.review_requirements
        show_statement_reviews = requirements.statement_reviewers > 0
        show_validator_reviews = requirements.validator_reviewers > 0
        show_data_reviews = requirements.data_reviewers > 0
        review_columns = (
            int(show_statement_reviews)
            + int(show_validator_reviews)
            + int(show_data_reviews)
        )
        if review_columns == 0:
            return
        num_columns = 1 + review_columns
        column_spec = "|l|" + "c|" * (num_columns - 1)
        with self.doc.create(Section("Manual review tracking", numbering=False)):
            with self.doc.create(Tabular(column_spec)) as table:
                table.add_hline()
                header_row = [NoEscape(r"{\tiny Problem}")]
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
                        Command("hyperref", (problem.name,), (f"sec:{problem.name}",))
                    ]
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
    def _coloured_cell(value: int, requirement: int) -> int | str | NoEscape:
        if requirement == 0:
            return value
        if value < requirement:
            return NoEscape(r"\cellcolor{insufficientred}" + f"{value}/{requirement}")
        else:
            return NoEscape(r"\cellcolor{sufficientgreen}" + f"{value}/{requirement}")

    @staticmethod
    def _oxford_list(items: list[str], connector: str):
        """Get a text list using the oxford comma."""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} {connector} {items[1]}"
        joined_names = ", ".join(items[:-1])
        return f"{joined_names}, {connector} {items[-1]}"

    def _oxford_and(self, items: list[str]):
        """Get a text 'and' list using the oxford comma."""
        return self._oxford_list(items, "and")

    def _oxford_or(self, items: list[str]):
        """Get a text 'or' list using the oxford comma."""
        return self._oxford_list(items, "or")

    def _add_independent_ac_needs(self, enum_env, problem):
        """Add text list of independent AC submission needs."""
        requirements = self.crifx_config.review_requirements
        if problem.independent_ac_count() < requirements.independent_ac:
            independent_needed = (
                requirements.independent_ac - problem.independent_ac_count()
            )
            ac_judge_names = {
                submission.author.primary_name for submission in problem.ac_submissions
            }
            if not ac_judge_names:
                if independent_needed == 1:
                    enum_env.add_item(f"{problem.name} needs an AC submission.")
                else:
                    enum_env.add_item(
                        f"{problem.name} needs {independent_needed} AC " f"submissions."
                    )
            elif independent_needed == 1:
                if requirements.independent_ac == 1:
                    enum_env.add_item(f"{problem.name} needs an AC submission.")
                else:
                    enum_env.add_item(
                        f"{problem.name} needs at least one more AC submission "
                        f"from someone other than "
                        f"{self._oxford_and(sorted(ac_judge_names))}."
                    )
            else:
                enum_env.add_item(
                    f"{problem.name} needs at least {independent_needed} more "
                    f"AC submissions from people other than "
                    f"{self._oxford_and(sorted(ac_judge_names))}."
                )

    def _add_language_group_ac_needs(self, enum_env, problem):
        """Add text list of language group AC submission needs."""
        requirements = self.crifx_config.review_requirements
        language_group_configs = self.crifx_config.language_group_configs
        language_groups = [
            group_config.language_group for group_config in language_group_configs
        ]
        groups_covered = problem.language_groups_ac_covered(language_groups)
        if len(groups_covered) < requirements.language_groups_ac:
            groups_needed_num = requirements.language_groups_ac - len(groups_covered)
            groups_not_covered_names = [
                config.identifier
                for config in language_group_configs
                if config.language_group not in groups_covered
            ]
            if groups_needed_num == 1:
                enum_env.add_item(
                    f"{problem.name} needs at least one more AC submission from "
                    f"any of the following language groups: "
                    f"{self._oxford_or(groups_not_covered_names)}."
                )
            else:
                enum_env.add_item(
                    f"{problem.name} needs at least {groups_needed_num} more AC "
                    f"submissions from any of the following language groups: "
                    f"{self._oxford_or(groups_not_covered_names)}."
                )

    def _add_tle_needs(self, enum_env, problem):
        """Add a text line for TLE submission needs for a problem."""
        requirements = self.crifx_config.review_requirements
        if len(problem.tle_submissions) < requirements.submissions_tle:
            tle_needed = requirements.submissions_tle - len(problem.tle_submissions)
            if requirements.submissions_tle == 1:
                enum_env.add_item(f"{problem.name} needs at least one TLE submission.")
            elif tle_needed == 1:
                enum_env.add_item(
                    f"{problem.name} needs at least one more TLE submission."
                )
            else:
                enum_env.add_item(
                    f"{problem.name} needs at least {tle_needed} more TLE "
                    f"submissions."
                )

    def _add_wa_needs(self, enum_env, problem):
        """Add a text line for WA submission needs for each problem."""
        requirements = self.crifx_config.review_requirements
        if len(problem.wa_submissions) < requirements.submissions_wa:
            wa_needed = requirements.submissions_wa - len(problem.wa_submissions)
            if requirements.submissions_wa == 1:
                enum_env.add_item(f"{problem.name} needs at least one WA submission.")
            elif wa_needed == 1:
                enum_env.add_item(
                    f"{problem.name} needs at least one more WA submission."
                )
            else:
                enum_env.add_item(
                    f"{problem.name} needs at least {wa_needed} more WA "
                    f"submissions."
                )

    def _add_review_needs(
        self, enum_env, problem_name, reviewers, required_count, review_type
    ):
        """Add an item for review needs of a given type."""
        if len(reviewers) < required_count:
            reviews_needed = required_count - len(reviewers)
            if not reviewers:
                if required_count == 1:
                    enum_env.add_item(
                        f"{problem_name} needs at least one {review_type} review."
                    )
                else:
                    enum_env.add_item(
                        f"{problem_name} needs at least {reviews_needed} "
                        f"{review_type} reviews."
                    )
            elif required_count == 1:
                enum_env.add_item(
                    f"{problem_name} needs at least one {review_type} review."
                )
            elif reviews_needed == 1:
                enum_env.add_item(
                    f"{problem_name} needs at least one more {review_type} review "
                    f"from someone other than {self._oxford_and(reviewers)}."
                )
            else:
                enum_env.add_item(
                    f"{problem_name} needs at least {reviews_needed} more "
                    f"{review_type} reviews from people other than "
                    f"{self._oxford_and(reviewers)}."
                )

    def _add_statement_review_needs(self, enum_env, problem):
        """Add an item for statement reviews needed for a problem."""
        requirements = self.crifx_config.review_requirements
        required_count = requirements.statement_reviewers
        reviewers = problem.review_status.statement_reviewed_by
        self._add_review_needs(
            enum_env, problem.name, reviewers, required_count, "statement"
        )

    def _add_data_review_needs(self, enum_env, problem):
        """Add an item for test data reviews needed for a problem."""
        requirements = self.crifx_config.review_requirements
        required_count = requirements.data_reviewers
        reviewers = problem.review_status.data_reviewed_by
        self._add_review_needs(
            enum_env, problem.name, reviewers, required_count, "test data"
        )

    def _add_validator_review_needs(self, enum_env, problem):
        """Add an item for validator reviews needed for each problem."""
        requirements = self.crifx_config.review_requirements
        required_count = requirements.validator_reviewers
        reviewers = problem.review_status.validators_reviewed_by
        self._add_review_needs(
            enum_env, problem.name, reviewers, required_count, "validator"
        )

    def _write_how_can_i_help(self):
        """Write the 'How can I help?' section."""
        with self.doc.create(Section("How can I help?", numbering=False)):
            with self.doc.create(Enumerate()) as enum_env:
                for problem in self.problem_set.problems:
                    self._add_independent_ac_needs(enum_env, problem)
                for problem in self.problem_set.problems:
                    self._add_language_group_ac_needs(enum_env, problem)
                for problem in self.problem_set.problems:
                    self._add_tle_needs(enum_env, problem)
                for problem in self.problem_set.problems:
                    self._add_wa_needs(enum_env, problem)
                for problem in self.problem_set.problems:
                    self._add_statement_review_needs(enum_env, problem)
                for problem in self.problem_set.problems:
                    self._add_validator_review_needs(enum_env, problem)
                for problem in self.problem_set.problems:
                    self._add_data_review_needs(enum_env, problem)
                enum_env.add_item("Add test data")
                enum_env.add_item("Add input validators")

    def _write_problem_details(self, problem: Problem):
        """Write the details for a problem."""
        assert self.doc is not None
        self.doc.append(Command(r"newpage"))
        with self.doc.create(Section(problem.name)):
            with self.doc.create(Subsection("How can I help?", numbering=False)):
                with self.doc.create(Enumerate()) as enum_env:
                    self._add_independent_ac_needs(enum_env, problem)
                    self._add_language_group_ac_needs(enum_env, problem)
                    self._add_tle_needs(enum_env, problem)
                    self._add_wa_needs(enum_env, problem)
                    self._add_statement_review_needs(enum_env, problem)
                    self._add_validator_review_needs(enum_env, problem)
                    self._add_data_review_needs(enum_env, problem)
            with self.doc.create(Subsection("Submissions", numbering=False)):
                with self.doc.create(Subsubsection("Accepted", numbering=False)):
                    if not problem.ac_submissions:
                        self.doc.append("No accepted submissions.")
                    with self.doc.create(Itemize()) as itemize:
                        for submission in problem.ac_submissions:
                            itemize.add_item(
                                f"{submission.filename} by {submission.author}. "
                                f"{submission.lines_of_code} lines of code."
                            )
                with self.doc.create(Subsubsection("Wrong Answer", numbering=False)):
                    if not problem.wa_submissions:
                        self.doc.append("No wrong answer submissions.")
                    with self.doc.create(Itemize()) as itemize:
                        for submission in problem.wa_submissions:
                            itemize.add_item(
                                f"{submission.filename} by {submission.author}. "
                                f"{submission.lines_of_code} lines of code."
                            )
                with self.doc.create(
                    Subsubsection("Time Limit Exceeded", numbering=False)
                ):
                    if not problem.tle_submissions:
                        self.doc.append("No time limit exceeded submissions.")
                    with self.doc.create(Itemize()) as itemize:
                        for submission in problem.tle_submissions:
                            itemize.add_item(
                                f"{submission.filename} by {submission.author}. "
                                f"{submission.lines_of_code} lines of code."
                            )
            with self.doc.create(Subsection("Test Cases", numbering=False)):
                self.doc.append(
                    "Test case descriptions are rendered below if .desc files exist."
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
