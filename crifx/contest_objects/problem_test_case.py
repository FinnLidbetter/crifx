"""Problem test case."""

import os
from dataclasses import dataclass


@dataclass
class ProblemTestCase:
    """Problem test case data."""

    name: str
    is_sample: bool
    dir_path: str
    description_lines: list[str]
    image_extension: str | None

    @property
    def has_description(self):
        """Return true if there is a nonempty description for the test case."""
        return bool(self.description_lines)

    def _get_path(self, extension) -> str:
        return os.path.join(self.dir_path, f"{self.name}.{extension}")

    @property
    def input_path(self) -> str:
        """Get the path to the input file."""
        return self._get_path("in")

    @property
    def answer_path(self) -> str:
        """Get the path to the answer file."""
        return self._get_path("ans")

    @property
    def description_path(self) -> str:
        """Get the path to the description file."""
        return self._get_path("desc")

    @property
    def image_path(self) -> str | None:
        """Get the path to the image file."""
        if self.image_extension is None:
            return None
        return self._get_path(self.image_extension)

    def sort_key(self) -> tuple[bool, str, str]:
        """Get the sort key for this test case."""
        return not self.is_sample, self.dir_path, self.name
