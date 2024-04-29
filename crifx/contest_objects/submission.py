"""Data structure for a problem submission."""

from dataclasses import dataclass

from crifx.contest_objects.author import Author
from crifx.contest_objects.judgement import Judgement
from crifx.contest_objects.programming_language import ProgrammingLanguage


@dataclass
class Submission:
    """Data structure for a problem submission."""

    author: Author
    path: str
    language: ProgrammingLanguage
    judgement: Judgement
    lines_of_code: int
