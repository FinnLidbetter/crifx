"""Logic for parsing a ProblemSet object from a git directory."""

import logging
import os

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
from crifx.git_manager import GitManager

TEST_CASE_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]


class ProblemSetParser:
    """Controller for parsing a ProblemSet object."""

    def __init__(self, problemset_root_path: str, git_manager: GitManager):
        if not is_contest_problems_root(problemset_root_path):
            raise ValueError(
                f"Path '{problemset_root_path}' is not a problemset root path."
            )
        self.problemset_root_path = problemset_root_path
        self.git_manager = git_manager
        self.judges_by_name: dict[str, Judge] = {}
        self._set_judges_by_name()

    def _set_judges_by_name(self):
        git_users = self.git_manager.get_committers_and_authors()
        git_users_by_name = {}
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
        self.judges_by_name = {
            git_user.name: Judge(git_user.name, git_user)
            for git_user in git_users_by_name.values()
        }

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
        submissions = self._parse_submissions(problem_root_dir)
        return Problem(name, problem_test_cases, submissions)

    def _parse_problem_test_cases(self, problem_root_dir: str) -> list[ProblemTestCase]:
        """Parse the problem test cases from a problem directory."""
        sample_data_dir = os.path.join(problem_root_dir, "data", "sample")
        secret_data_dir = os.path.join(problem_root_dir, "data", "secret")
        return self._parse_test_case_dir(sample_data_dir) + self._parse_test_case_dir(
            secret_data_dir
        )

    def _parse_test_case_dir(self, test_case_dir: str):
        """Parse the test cases from a test case directory."""
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
                    "Input file %s.in has no corresponding .ans file.", in_filename
                )
        for ans_filename in ans_files:
            if ans_filename not in in_files:
                logging.warning(
                    "Answer file %s.ans has no corresponding .in file.", ans_filename
                )
        for filename in in_files:
            if filename not in ans_files:
                continue
            name = filename
            is_sample = test_case_dir.startswith("sample")
            input_lines = []
            ans_lines: list[str] = []
            desc_lines = []
            image_extension = None
            try:
                input_file_path = os.path.join(test_case_dir, f"{filename}.in")
                ans_file_path = os.path.join(test_case_dir, f"{filename}.ans")
                desc_file_path = os.path.join(test_case_dir, f"{filename}.desc")
                image_extension = None
                for extension in TEST_CASE_IMAGE_EXTENSIONS:
                    if os.path.exists(
                        os.path.join(test_case_dir, f"{filename}.{extension}")
                    ):
                        image_extension = extension
                        break
                with open(input_file_path) as input_file:
                    input_lines = list(input_file.readlines())
                with open(ans_file_path) as answer_file:
                    ans_lines = list(answer_file.readlines())
                if os.path.exists(desc_file_path):
                    with open(desc_file_path) as desc_file:
                        desc_lines = list(desc_file.readlines())
            except (FileExistsError, FileNotFoundError, PermissionError):
                logging.exception("Test case file could not be read.")
            test_case = ProblemTestCase(
                name,
                is_sample,
                test_case_dir,
                input_lines,
                ans_lines,
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
            git_user = self.git_manager.guess_file_author(submission_path)
            judge = self.judges_by_name.get(getattr(git_user, "name")) or UNKNOWN_JUDGE
            lines_of_code = 0
            file_bytes = 0
            try:
                with open(submission_path, "r") as submission_file:
                    lines_of_code = len(submission_file.readlines())
                file_bytes = os.stat(submission_path).st_size
            except (FileExistsError, FileNotFoundError, PermissionError):
                logging.warning(
                    "Could not determine size of submission at path '%s'",
                    submission_path,
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
