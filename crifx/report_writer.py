"""Module for writing the report to file."""

import io


def write_report(write_handle: io.TextIOWrapper | io.TextIOBase):
    """Write the report at the given file handle."""
    write_handle.writelines(["Hello world!"])
