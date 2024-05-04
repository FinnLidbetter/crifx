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
    assert len(problemset.problems) == 2
    assert len(problemset.problems[0].test_cases) == 5
    assert problemset.problems[0].test_cases
    desc_test_cases = list(
        filter(lambda x: x.has_description, problemset.problems[0].test_cases)
    )
    assert len(desc_test_cases) == 1
    desc_test_case = desc_test_cases[0]
    assert desc_test_case.name == "2"
    assert desc_test_case.dir_path.endswith("data/secret")
    assert desc_test_case.input_lines == ["Secret case\n", "with more than one line"]
    assert desc_test_case.answer_lines == ["Hello world!"]
    assert desc_test_case.description_lines == [
        "Secret test case\n",
        "\n",
        "this is a description with a blank line\n",
    ]
    assert desc_test_case.image_extension is None
    assert len(problemset.problems[0].submissions) == 3
    assert len(problemset.problems[0].ac_submissions) == 2
    assert len(problemset.problems[0].wa_submissions) == 1
    assert len(problemset.problems[0].tle_submissions) == 0
