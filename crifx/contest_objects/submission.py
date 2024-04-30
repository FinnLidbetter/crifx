"""Data structure for a problem submission."""

from dataclasses import dataclass

from crifx.contest_objects.judge import Judge
from crifx.contest_objects.judgement import Judgement
from crifx.contest_objects.programming_language import ProgrammingLanguage


@dataclass
class Submission:
    """Data structure for a problem submission."""

    author: Judge
    filename: str
    language: ProgrammingLanguage
    judgement: Judgement
    lines_of_code: int
    bytes_count: int
