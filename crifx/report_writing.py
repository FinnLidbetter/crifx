"""Module for writing the report to file."""

import contextlib
import io
import os
import sys

REPORT_FILENAME = "report.tex"


@contextlib.contextmanager
def smart_open(filename=None):
    """Context manager for getting a file handle for writing to file or stdout."""
    if filename and filename != "-":
        file_handle = open(filename, "w")
    else:
        file_handle = sys.stdout

    try:
        yield file_handle
    finally:
        if file_handle is not sys.stdout:
            file_handle.close()


def make_crifx_dir(containing_dir_path: str):
    """Create the crifx directory."""
    crifx_dir_path = os.path.join(containing_dir_path, ".crifx")
    if not os.path.exists(crifx_dir_path):
        os.mkdir(crifx_dir_path)
    return crifx_dir_path


def write_report(write_handle: io.TextIOBase):
    """Write the report at the given file handle."""
    write_handle.writelines(["Hello world!"])
