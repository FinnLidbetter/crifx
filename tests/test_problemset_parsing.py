"""Tests for parsing problemsets."""

import os

from crifx.git_manager import GitManager
from crifx.problemset_parser import ProblemSetParser


def test_scenario_1(scenarios_path):
    """Test the basic scenario 1."""
    path = os.path.join(scenarios_path, "sample_contest_1")
    git_manager = GitManager(scenarios_path)
    parser = ProblemSetParser(path, git_manager)
    problemset = parser.parse_problemset()
    assert len(problemset.problems) == 1
