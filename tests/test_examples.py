"""Tests for the example problemsets."""

import os


def test_example_problemset(examples_path):
    """Test that the example problemset is being parsed as expected."""
    example_problemset_path = os.path.join(examples_path, "example_problemset")
    example_test_output = os.path.join(example_problemset_path, ".test_output")
    status = os.system(
        f"crifx {example_problemset_path} --output-dir {example_test_output}"
    )
    assert status == 0
