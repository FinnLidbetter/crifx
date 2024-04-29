"""Data structure and manager for a problem set."""

from crifx.contest_objects.author import Author
from crifx.contest_objects.problem import Problem


class ProblemSet:
    """Data structure and manager for a problem set."""

    def __init__(self, problems: list[Problem]):
        self.problems = problems

    def submission_authors(self) -> list[Author]:
        """Get the set of authors that have contributed at least one submission."""
        authors = set()
        for problem in self.problems:
            for submission in problem.submissions:
                authors.add(submission.author)
        return sorted(authors, key=lambda x: x.primary_name)
