"""Tests for writing the report."""

import os

from crifx import write_report


def test_write_report(tmp_path):
    """A report tex file is can be written to the expected path."""
    assert not os.listdir(tmp_path)
    write_report(tmp_path)
    expected_file = "crifx-report.tex"
    assert expected_file in os.listdir(tmp_path)
    report_path = os.path.join(tmp_path, expected_file)
    with open(report_path, "r") as tmp_file:
        lines = tmp_file.readlines()
    expected_title = "\\title{CRIFX Contest Preparation Status Report}%\n"
    assert expected_title in lines
