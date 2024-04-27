"""Pytest fixtures."""

import os
import shutil
import uuid

import pytest


@pytest.fixture
def tmp_file_path(tmp_path):
    """Get a unique file path in a tmp directory."""
    unique_id = str(uuid.uuid4())
    tmp_file = os.path.join(tmp_path, f"crifx-{unique_id}.txt")
    yield tmp_file
    os.remove(tmp_file)


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
