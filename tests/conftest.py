"""Pytest fixtures."""

import os
import uuid

import pytest

from crifx.contest_objects import Judge, Judgement, ProgrammingLanguage, Submission
from crifx.git_manager import GitUser


@pytest.fixture
def tmp_file_path(tmp_path):
    """Get a unique file path in a tmp directory."""
    unique_id = str(uuid.uuid4())
    tmp_file = os.path.join(tmp_path, f"crifx-{unique_id}.txt")
    yield tmp_file
    os.remove(tmp_file)


@pytest.fixture
def examples_path(pytestconfig):
    """Get the path to the examples directory."""
    yield os.path.join(pytestconfig.rootpath, "examples")


@pytest.fixture
def scenarios_path(pytestconfig):
    """Get the path to the scenarios directory."""
    yield os.path.join(pytestconfig.rootpath, "tests", "scenarios")


@pytest.fixture
def make_problem_skeleton_dir(tmp_path):
    """Make a problem directory skeleton."""

    def _func() -> str:
        problem_name = f"problem-{str(uuid.uuid4())}"
        problem_path = os.path.join(tmp_path, problem_name)
        os.mkdir(problem_path)
        os.makedirs(os.path.join(problem_path, "data/sample"))
        os.makedirs(os.path.join(problem_path, "data/secret"))
        os.makedirs(os.path.join(problem_path, "submissions/accepted"))
        os.mkdir(os.path.join(problem_path, "problem_statement"))
        os.mkdir(os.path.join(problem_path, "input_format_validators"))
        return problem_path

    yield _func


@pytest.fixture
def make_judged_lang_submission():
    """Make a submission with a given judgement and programming language."""

    def _func(judgement: Judgement, language: ProgrammingLanguage) -> Submission:
        return Submission(Judge("name", None), "solution", language, judgement, 1, 1)

    yield _func


@pytest.fixture
def make_authored_submission():
    """Make a submission with a Judge with the given primary name and git name."""

    def _func(
        primary_name: str,
        git_name: str | None,
        judgement: Judgement = Judgement.ACCEPTED,
        language: ProgrammingLanguage = ProgrammingLanguage.JAVA,
    ) -> Submission:
        if git_name is None:
            judge = Judge(primary_name, None)
        else:
            git_email = f"{git_name}@example.com"
            git_user = GitUser(
                git_name, git_email, str.encode(git_name), str.encode(git_email)
            )
            judge = Judge(primary_name, git_user)
        return Submission(judge, "solution", language, judgement, 0, 0)

    yield _func
