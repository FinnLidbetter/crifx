"""Tests for parsing problemsets."""

import os

from crifx.config_parser import parse_config
from crifx.contest_objects import ProgrammingLanguage
from crifx.git_manager import GitManager
from crifx.problemset_parser import ProblemSetParser


def test_scenario_1(scenarios_path):
    """Test the basic scenario 1."""
    path = os.path.join(scenarios_path, "sample_contest_1")
    git_manager = GitManager(scenarios_path)
    config = parse_config(path)
    parser = ProblemSetParser(path, git_manager, config.alias_groups, False)
    problemset = parser.parse_problemset()
    problem_a = next(
        problem for problem in problemset.problems if problem.name == "problem_a"
    )
    assert len(problemset.problems) == 2
    assert len(problem_a.test_cases) == 5
    a_desc_test_cases = list(filter(lambda x: x.has_description, problem_a.test_cases))
    assert len(a_desc_test_cases) == 1
    desc_test_case = a_desc_test_cases[0]
    assert desc_test_case.name == "2"
    assert desc_test_case.dir_path.endswith("data/secret")
    assert desc_test_case.description_lines == [
        "Secret test case\n",
        "\n",
        "this is a description with a blank line\n",
    ]
    assert desc_test_case.image_extension is None
    assert len(problem_a.submissions) == 3
    assert len(problem_a.ac_submissions) == 2
    assert len(problem_a.wa_submissions) == 1
    assert len(problem_a.tle_submissions) == 0

    problem_a_java_ac = next(
        sub
        for sub in problem_a.ac_submissions
        if sub.language is ProgrammingLanguage.JAVA
    )
    assert problem_a_java_ac.author.primary_name == "Jane Doe"
