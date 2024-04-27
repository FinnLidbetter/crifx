"""Tests for file hierarchy parsing."""

import os
import unittest.mock as mock
import uuid

from crifx.dir_layout_parsing import (
    find_contest_problems_root,
    get_problem_root_dirs,
    is_contest_problems_root,
    is_problem_root_dir,
)


def test_is_problem_root_dir(tmp_path):
    """Test detecting a problem directory."""
    # A directory with a submissions directory inside is a problem root dir.
    dir_1 = os.path.join(tmp_path, str(uuid.uuid4()))
    os.mkdir(dir_1)
    os.mkdir(os.path.join(dir_1, "submissions"))
    assert is_problem_root_dir(dir_1)

    # A directory with a problem_statement directory inside is a problem root dir.
    dir_2 = os.path.join(tmp_path, str(uuid.uuid4()))
    os.mkdir(dir_2)
    os.mkdir(os.path.join(dir_2, "problem_statement"))
    assert is_problem_root_dir(dir_2)

    # A directory with a problem.yaml file is a problem root dir.
    dir_3 = os.path.join(tmp_path, str(uuid.uuid4()))
    os.mkdir(dir_3)
    open(os.path.join(dir_3, "problem.yaml"), "a").close()
    assert is_problem_root_dir(dir_3)

    # A directory with a problem.yml file is a problem root dir.
    dir_4 = os.path.join(tmp_path, str(uuid.uuid4()))
    os.mkdir(dir_4)
    open(os.path.join(dir_4, "problem.yml"), "a").close()
    assert is_problem_root_dir(dir_4)

    # Dir with no submissions, problem_statement, nor problem yaml is not problem root.
    dir_5 = os.path.join(tmp_path, str(uuid.uuid4()))
    os.mkdir(dir_5)
    os.mkdir(os.path.join(dir_5, "data"))
    assert not is_problem_root_dir(dir_5)

    # Non-dir file is not a problem root dir.
    tmp_file = os.path.join(tmp_path, f"{str(uuid.uuid4())}.txt")
    open(tmp_file, "a").close()
    assert not is_problem_root_dir(tmp_file)


def test_get_problem_root_dirs(tmp_path, make_problem_skeleton_dir):
    """Contest problem paths can be identified in a contest problems directory."""
    assert not os.listdir(tmp_path)
    # Set up a couple of problems.
    path_1 = make_problem_skeleton_dir()
    path_2 = make_problem_skeleton_dir()
    # Problem skeletons were set up in the tmp_path.
    assert os.listdir(tmp_path)
    # Add some other arbitrary files.
    open(os.path.join(tmp_path, "problemset.pdf"), "a").close()
    open(os.path.join(tmp_path, "random_file.txt"), "a").close()
    assert is_contest_problems_root(tmp_path)
    assert sorted(get_problem_root_dirs(tmp_path)) == sorted([path_1, path_2])


def test_find_contest_problem_root(tmp_path, make_problem_skeleton_dir):
    """The contest problem root can be found from inside nested directories."""
    assert not os.listdir(tmp_path)
    problem_path = make_problem_skeleton_dir()
    assert os.listdir(tmp_path)
    with mock.patch(
        "os.getcwd", return_value=os.path.join(problem_path, "submissions/accepted")
    ):
        assert find_contest_problems_root() == str(tmp_path)
    with mock.patch(
        "os.getcwd", return_value=os.path.join(problem_path, "submissions")
    ):
        assert find_contest_problems_root() == str(tmp_path)
    with mock.patch(
        "os.getcwd", return_value=os.path.join(problem_path, "submissions/data/secret")
    ):
        assert find_contest_problems_root() == str(tmp_path)
