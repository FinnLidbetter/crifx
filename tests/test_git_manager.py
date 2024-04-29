"""Tests for the GitManager class."""

import os

from crifx.git_manager import GitManager


def test_guess_file_author():
    """The guess_file_author method returns a git user."""
    path = os.path.join(
        "tests",
        "scenarios",
        "sample_contest_1",
        "problem_a",
        "submissions",
        "accepted",
        "hello_world.py",
    )
    git_manager = GitManager(os.getcwd())

    git_user = git_manager.guess_file_author(path)
    assert git_user.name == "Finn Lidbetter"
