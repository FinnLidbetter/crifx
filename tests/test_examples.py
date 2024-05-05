"""Tests for the example problemsets."""

import os


def test_example_problemset(examples_path):
    """Test that the example problemset is being parsed as expected."""
    example_problemset_path = os.path.join(examples_path, "example_problemset")
