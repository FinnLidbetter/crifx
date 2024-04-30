"""Data structure for data about a problem."""

from collections import defaultdict
from dataclasses import dataclass

from crifx.contest_objects.judge import Judge
from crifx.contest_objects.judgement import Judgement
from crifx.contest_objects.problem_test_case import ProblemTestCase
from crifx.contest_objects.programming_language import ProgrammingLanguage
from crifx.contest_objects.submission import Submission


@dataclass
class Problem:
    """Data for a Problem."""

    name: str
    test_data: list[ProblemTestCase]
    submissions: list[Submission]

    def _get_submissions_with_judgement(self, judgement):
        return list(filter(lambda x: x.judgement is judgement, self.submissions))

    @property
    def ac_submissions(self) -> list[Submission]:
        """Get the AC submissions."""
        return self._get_submissions_with_judgement(Judgement.ACCEPTED)

    @property
    def wa_submissions(self) -> list[Submission]:
        """Get the WA submissions."""
        return self._get_submissions_with_judgement(Judgement.WRONG_ANSWER)

    @property
    def tle_submissions(self) -> list[Submission]:
        """Get the TLE submissions."""
        return self._get_submissions_with_judgement(Judgement.TIME_LIMIT_EXCEEDED)

    @property
    def rte_submissions(self) -> list[Submission]:
        """Get the RTE submissions."""
        return self._get_submissions_with_judgement(Judgement.RUN_TIME_ERROR)

    def independent_ac_count(self) -> int:
        """Get the number of AC submissions by different authors."""
        accepted_authors: list[Judge] = []
        for submission in self.ac_submissions:
            if any(submission.author.is_same(author) for author in accepted_authors):
                continue
            accepted_authors.append(submission.author)
        return len(accepted_authors)

    def ac_languages(self) -> defaultdict[ProgrammingLanguage, int]:
        """Get the number of AC submissions in each language."""
        language_counts: defaultdict[ProgrammingLanguage, int] = defaultdict(int)
        for submission in self.ac_submissions:
            language_counts[submission.language] += 1
        return language_counts
