"""Pytest fixtures."""

import os
import uuid
import zipfile
from pathlib import Path

import pygit2
import pytest

from crifx.contest_objects import Judge, Judgement, ProgrammingLanguage, Submission
from crifx.git_manager import GitUser


@pytest.fixture(scope="session", autouse=True)
def remove_git_config_paths():
    """Remove git configurations from pygit2 to improve test reproducibility."""
    levels = [
        pygit2.enums.ConfigLevel.GLOBAL,
        pygit2.enums.ConfigLevel.XDG,
        pygit2.enums.ConfigLevel.SYSTEM,
    ]
    for level in levels:
        pygit2.settings.search_path[level] = ""


class TemporaryRepository:
    """
    Context managed class for creating a repository at a temporary path.

    The provided name must be a .zip file name.
    """

    def __init__(self, name, tmp_path):
        self.name = name
        self.tmp_path = tmp_path

    def __enter__(self):
        path = Path(__file__).parent.joinpath("data", self.name)
        temp_repo_path = Path(self.tmp_path).joinpath(path.stem)
        with zipfile.ZipFile(path) as zipped_data_file:
            zipped_data_file.extractall(self.tmp_path)
        return temp_repo_path

    def __exit__(self, exc_type, exc_value, traceback):
        pass


@pytest.fixture
def empty_repo(tmp_path):
    """Initialise a temporary empty (but non-bare) repository."""
    with TemporaryRepository("empty_repo.zip", tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def global_git_config_path(tmp_path):
    """Set and return a global git config path."""
    level = pygit2.enums.ConfigLevel.GLOBAL
    pygit2.settings.search_path[level] = str(tmp_path)
    yield os.path.join(tmp_path, ".gitconfig")


@pytest.fixture
def tmp_file_path(tmp_path):
    """Get a unique file path in a tmp directory."""
    unique_id = str(uuid.uuid4())
    tmp_file = os.path.join(tmp_path, f"crifx-{unique_id}.txt")
    yield tmp_file
    os.remove(tmp_file)


@pytest.fixture
def make_file_at_path():
    """Write a file in the provided directory and delete it afterwards."""
    written_files = []

    def _func(dir_path):
        unique_id = str(uuid.uuid4())
        file_name = f"crifx-tmp_file-{unique_id}.txt"
        file_path = os.path.join(dir_path, file_name)
        open(file_path, "a").close()
        written_files.append(file_path)
        return file_path

    yield _func
    for file in written_files:
        os.remove(file)


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
