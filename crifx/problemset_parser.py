"""Logic for parsing a ProblemSet object from a git directory."""

import logging
import os
import re
import tomllib
from typing import Any, Optional

from crifx.config_parser import AliasGroup
from crifx.contest_objects import (
    UNKNOWN_JUDGE,
    Judge,
    Judgement,
    Problem,
    ProblemSet,
    ProblemTestCase,
    ProgrammingLanguage,
    Submission,
)
from crifx.dir_layout_parsing import get_problem_root_dirs, is_contest_problems_root
from crifx.git_manager import GitManager, GitUser
from crifx.report_objects import (
    DEFAULT_REVIEW_STATUS,
    DEFAULT_REVIEW_STATUS_TOML,
    ReviewStatus,
)

TEST_CASE_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]
PROBLEM_REVIEW_STATUS_FILENAME = "crifx-problem-status.toml"
CRIFX_AUTHOR_PATTERN = "crifx!\(author=([a-zA-Z0-9_ ]+)\)"


class ProblemSetParser:
    """Controller for parsing a ProblemSet object."""

    def __init__(
        self,
        problemset_root_path: str,
        git_manager: GitManager,
        alias_groups: list[AliasGroup],
        track_review_status: bool,
    ):
        if not is_contest_problems_root(problemset_root_path):
            raise ValueError(
                f"Path '{problemset_root_path}' is not a problemset root path."
            )
        self.problemset_root_path = problemset_root_path
        self.git_manager = git_manager
        self.track_review_status = track_review_status
        self.judges_by_name: dict[str, Judge] = {}
        self._set_judges_by_name(alias_groups)

    def _set_judges_by_name(self, alias_groups: list[AliasGroup]):
        git_users = self.git_manager.get_committers_and_authors()
        git_users_by_name: dict[str, GitUser] = {}
        for user in git_users:
            if user.name in git_users:
                logging.warning(
                    "Multiple users with name %s: (%s), (%s). "
                    "Commits from these users may be reported as from the same person.",
                    user.name,
                    git_users_by_name[user.name],
                    user,
                )
            git_users_by_name[user.name] = user
        gitless = []
        aliases_by_git_name = {}
        for alias_group in alias_groups:
            if alias_group.git_name is not None:
                aliases_by_git_name[alias_group.git_name] = alias_group.aliases
            else:
                gitless.append(alias_group)
        self.judges_by_name = {
            git_user.name: Judge(
                git_user.name, git_user, *aliases_by_git_name.get(git_user.name, [])
            )
            for git_user in git_users_by_name.values()
        }
        for alias_group in alias_groups:
            if (
                alias_group.git_name is not None
                and alias_group.git_name not in self.judges_by_name
            ):
                # The user has a git name but no commits in the repository yet.
                self.judges_by_name[alias_group.git_name] = Judge(
                    alias_group.identifier,
                    GitUser(alias_group.git_name, "unknown email", b"", b""),
                    *alias_group.aliases,
                )
        for alias_group in gitless:
            if alias_group.identifier in git_users_by_name:
                logging.warning(
                    "Add a 'git_name' for judge '%s' in the crifx configuration "
                    "file to use their aliases.",
                    alias_group.identifier,
                )
            else:
                self.judges_by_name[alias_group.identifier] = Judge(
                    alias_group.identifier, None, *alias_group.aliases
                )
        logging.debug("Identified judges: %s", str(self.judges_by_name))

    def parse_problemset(self) -> ProblemSet:
        """Parse a ProblemSet."""
        problem_root_dirs = get_problem_root_dirs(self.problemset_root_path)
        problems = []
        for problem_root_dir in problem_root_dirs:
            problem = self._parse_problem(problem_root_dir)
            problems.append(problem)
        return ProblemSet(problems)

    def _parse_problem(self, problem_root_dir: str) -> Problem:
        """Parse a problem object from a problem directory."""
        _, name = os.path.split(problem_root_dir)
        problem_test_cases = self._parse_problem_test_cases(problem_root_dir)
        problem_test_cases.sort(key=lambda x: x.sort_key())
        submissions = self._parse_submissions(problem_root_dir)
        review_status = self._parse_review_status(problem_root_dir)
        return Problem(name, problem_test_cases, submissions, review_status)

    def _parse_problem_test_cases(self, problem_root_dir: str) -> list[ProblemTestCase]:
        """Parse the problem test cases from a problem directory."""
        sample_data_dir = os.path.join(problem_root_dir, "data", "sample")
        secret_data_dir = os.path.join(problem_root_dir, "data", "secret")
        return self._parse_test_case_dir(sample_data_dir) + self._parse_test_case_dir(
            secret_data_dir
        )

    def _parse_test_case_dir(self, test_case_dir: str):
        """Parse the test cases from a test case directory."""
        if not os.path.exists(test_case_dir):
            return []
        in_files = set()
        ans_files = set()
        test_cases = []
        for filename in os.listdir(test_case_dir):
            file_path = os.path.join(test_case_dir, filename)
            if os.path.isfile(file_path):
                if filename.endswith(".in"):
                    in_files.add(filename[:-3])
                elif filename.endswith(".ans"):
                    ans_files.add(filename[:-4])
            elif os.path.isdir(file_path):
                nested_dir = os.path.join(test_case_dir, filename)
                test_cases.extend(self._parse_test_case_dir(nested_dir))
        for in_filename in in_files:
            if in_filename not in ans_files:
                logging.warning(
                    "Input file %s.in has no corresponding .ans file.",
                    os.path.join(test_case_dir, in_filename),
                )
        for ans_filename in ans_files:
            if ans_filename not in in_files:
                logging.warning(
                    "Answer file %s.ans has no corresponding .in file.",
                    os.path.join(test_case_dir, ans_filename),
                )
        for filename in in_files:
            if filename not in ans_files:
                continue
            name = filename
            is_sample = test_case_dir.startswith("sample")
            desc_lines = []
            image_extension = None
            try:
                desc_file_path = os.path.join(test_case_dir, f"{filename}.desc")
                image_extension = None
                for extension in TEST_CASE_IMAGE_EXTENSIONS:
                    if os.path.exists(
                        os.path.join(test_case_dir, f"{filename}.{extension}")
                    ):
                        image_extension = extension
                        break
                if os.path.exists(desc_file_path):
                    with open(desc_file_path) as desc_file:
                        desc_lines = list(desc_file.readlines())
            except (FileExistsError, FileNotFoundError, PermissionError):
                logging.exception("Test case file could not be read.")
            test_case = ProblemTestCase(
                name,
                is_sample,
                test_case_dir,
                desc_lines,
                image_extension,
            )
            test_cases.append(test_case)
        return test_cases

    def _parse_submissions(self, problem_root_dir: str) -> list[Submission]:
        """Parse the submissions from a problem directory."""
        ac_dir = os.path.join(problem_root_dir, "submissions", "accepted")
        wa_dir = os.path.join(problem_root_dir, "submissions", "wrong_answer")
        tle_dir = os.path.join(problem_root_dir, "submissions", "time_limit_exceeded")
        rte_dir = os.path.join(problem_root_dir, "submissions", "run_time_error")
        submissions = []
        submissions.extend(self._parse_submissions_dir(ac_dir, Judgement.ACCEPTED))
        submissions.extend(self._parse_submissions_dir(wa_dir, Judgement.WRONG_ANSWER))
        submissions.extend(
            self._parse_submissions_dir(tle_dir, Judgement.TIME_LIMIT_EXCEEDED)
        )
        submissions.extend(
            self._parse_submissions_dir(rte_dir, Judgement.RUN_TIME_ERROR)
        )
        return submissions

    def _parse_submissions_dir(
        self, submissions_dir: str, judgement: Judgement
    ) -> list[Submission]:
        """Parse the Submission objects from a directory."""
        if not os.path.exists(submissions_dir):
            return []
        submissions = []
        for filename in os.listdir(submissions_dir):
            language = ProgrammingLanguage.from_filename(filename)
            if language is None:
                continue
            submission_path = os.path.join(submissions_dir, filename)
            lines_of_code = 0
            file_bytes = 0
            author_name_override = None
            try:
                with open(submission_path, "r") as submission_file:
                    submission_lines = submission_file.readlines()
                    for line_number, line in enumerate(submission_lines):
                        author_match = re.search(CRIFX_AUTHOR_PATTERN, line)
                        if author_match is not None:
                            author_name_override = author_match.group(1)
                            logging.debug(
                                "Found author override for file %s on line %d. Override name is '%s'",
                                submission_path,
                                line_number + 1,
                                author_name_override,
                            )
                            break
                    lines_of_code = len(submission_lines)
                file_bytes = os.stat(submission_path).st_size
            except (FileExistsError, FileNotFoundError, PermissionError):
                logging.warning(
                    "Could not determine size of submission at path '%s'",
                    submission_path,
                )
            git_user_guess = self.git_manager.guess_file_author(submission_path)
            filename_guess = self.guess_author_by_filename(filename)
            if author_name_override is not None:
                judge = UNKNOWN_JUDGE
                for candidate_judge in self.judges_by_name.values():
                    if candidate_judge.has_alias(author_name_override):
                        judge = candidate_judge
                        break
            elif filename_guess is not None:
                judge = filename_guess

            else:
                judge = (
                    self.judges_by_name.get(getattr(git_user_guess, "name"))
                    or UNKNOWN_JUDGE
                )
            submission = Submission(
                judge,
                filename,
                language,
                judgement,
                lines_of_code,
                file_bytes,
            )
            submissions.append(submission)
        return submissions

    def _parse_review_status(
        self,
        problem_root_dir: str,
    ) -> ReviewStatus:
        """Parse the problem review status."""
        if not self.track_review_status:
            return DEFAULT_REVIEW_STATUS
        review_status_path = os.path.join(
            problem_root_dir,
            PROBLEM_REVIEW_STATUS_FILENAME,
        )
        if not os.path.exists(review_status_path):
            with open(review_status_path, "w") as review_status_file:
                review_status_file.write(DEFAULT_REVIEW_STATUS_TOML)
        try:
            with open(review_status_path, "rb") as review_status_file:
                toml_dict = tomllib.load(review_status_file)
        except (PermissionError, FileNotFoundError, FileExistsError):
            logging.exception(
                "Failed to read problem review status file at path '%s'.",
                review_status_path,
            )
            return DEFAULT_REVIEW_STATUS
        github_issue_id = toml_dict.get("github_issue_id")
        if not isinstance(github_issue_id, int):
            github_issue_id = None
        review_status_dict = toml_dict.get("review_status", {})
        statement_reviewed_by = _read_reviewers(
            review_status_dict, "statement_reviewed_by", review_status_path
        )
        validators_reviewed_by = _read_reviewers(
            review_status_dict, "validators_reviewed_by", review_status_path
        )
        data_reviewed_by = _read_reviewers(
            review_status_dict, "data_reviewed_by", review_status_path
        )
        return ReviewStatus(
            github_issue_id,
            statement_reviewed_by,
            validators_reviewed_by,
            data_reviewed_by,
        )

    def guess_author_by_filename(self, filename) -> Judge | None:
        """Guess the author of a file based on the filename and configured aliases."""
        if "." in filename:
            filename_without_extension = filename[: filename.rindex(".")]
        else:
            filename_without_extension = filename
        underscore_split_filename = filename_without_extension.split("_")
        for part in underscore_split_filename:
            for judge in self.judges_by_name.values():
                if judge.has_alias(part):
                    return judge
        return None


def _read_reviewers(
    review_status_dict: dict[str, Any], reviewer_str: str, path: str
) -> list[str]:
    """Get a list of reviewers strings from a toml dictionary."""
    reviewers = review_status_dict.get(reviewer_str, [])
    if not isinstance(reviewers, list) or not all(
        isinstance(val, str) for val in reviewers
    ):
        logging.error(
            "%s [review_status] %s should be a list of strings, but instead it is %s",
            path,
            reviewer_str,
            reviewers,
        )
        reviewers = []
    return reviewers
