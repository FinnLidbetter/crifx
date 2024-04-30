"""Problem test case."""

import os
from dataclasses import dataclass


@dataclass
class ProblemTestCase:
    """Problem test case data."""

    name: str
    is_sample: bool
    input_lines: list[str]
    answer_lines: list[str]
    description_lines: list[str]
    image_extension: str | None

    @property
    def has_description(self):
        """Return true if there is a nonempty description for the test case."""
        return bool(self.description_lines)

    def _get_path(self, extension) -> str:
        if self.is_sample:
            return os.path.join("sample", f"{self.name}.{extension}")
        else:
            return os.path.join("secret", f"{self.name}.{extension}")

    @property
    def input_path(self) -> str:
        """Get the path relative to `/data/` for the input file."""
        return self._get_path("in")

    @property
    def answer_path(self) -> str:
        """Get the path relative to `/data/` for the answer file."""
        return self._get_path("ans")

    @property
    def description_path(self) -> str:
        """Get the path relative to `/data/` for the description file."""
        return self._get_path("desc")

    @property
    def image_path(self) -> str | None:
        """Get the path relative to `/data/` for the image file."""
        if self.image_extension is None:
            return None
        return self._get_path(self.image_extension)
