"""Data structure and manager for a problem set."""

from crifx.contest_objects.judge import Judge
from crifx.contest_objects.problem import Problem


class ProblemSet:
    """Data structure and manager for a problem set."""

    def __init__(self, problems: list[Problem]):
        sorted_problems = sorted(problems, key=lambda x: x.name)
        self.problems = sorted_problems

    def submission_authors(self) -> list[Judge]:
        """Get the set of authors that have contributed at least one submission."""
        authors = set()
        for problem in self.problems:
            for submission in problem.submissions:
                authors.add(submission.author)
        return sorted(authors, key=lambda x: x.primary_name)
