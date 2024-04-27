"""Pytest fixtures."""

import os
import uuid

import pytest


@pytest.fixture
def tmp_file_path(tmp_path):
    """Get a unique file path in a tmp directory."""
    unique_id = str(uuid.uuid4())
    tmp_file = os.path.join(tmp_path, f"crifx-{unique_id}.txt")
    yield tmp_file
    os.remove(tmp_file)
