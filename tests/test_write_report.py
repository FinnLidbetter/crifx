"""Tests for writing the report."""


from crifx import write_report


def test_write_report(tmp_file_path):
    """Writing a report to fix works."""
    with open(tmp_file_path, 'w') as tmp_file:
        write_report(tmp_file)
    with open(tmp_file_path, 'r') as tmp_file:
        lines = tmp_file.readlines()
    assert "Hello world!" in lines
