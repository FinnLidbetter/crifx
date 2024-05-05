"""Tests for writing the report."""

import os

from crifx.config_parser import Config
from crifx.contest_objects import ProblemSet
from crifx.git_manager import GitManager
from crifx.report_writer import ReportWriter


def test_write_report(tmp_path, scenarios_path):
    """A report tex file can be written to the expected path."""
    assert not os.listdir(tmp_path)
    problemset = ProblemSet([])
    git_manager = GitManager(scenarios_path)
    config = Config({})
    writer = ReportWriter(problemset, config, git_manager)
    writer.build_report(tmp_path)
    writer.write_tex(tmp_path)
    expected_file = "crifx-report.tex"
    assert expected_file in os.listdir(tmp_path)
    report_path = os.path.join(tmp_path, expected_file)
    with open(report_path, "r") as tmp_file:
        lines = tmp_file.readlines()
    expected_title = "\\title{CRIFX Contest Preparation Status Report}%\n"
    assert expected_title in lines
