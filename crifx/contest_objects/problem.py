"""Data structure for data about a problem."""

from collections import defaultdict
from dataclasses import dataclass

from crifx.contest_objects.judge import Judge
from crifx.contest_objects.judgement import Judgement
from crifx.contest_objects.problem_test_case import ProblemTestCase
from crifx.contest_objects.programming_language import (
    LanguageGroup,
    ProgrammingLanguage,
)
from crifx.contest_objects.submission import Submission
from crifx.report_objects import ReviewStatus


@dataclass(frozen=True)
class Problem:
    """Data for a Problem."""

    name: str
    test_cases: list[ProblemTestCase]
    submissions: list[Submission]
    review_status: ReviewStatus

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

    def language_groups_ac_covered(self, language_groups: list[LanguageGroup]):
        """Get the number of language groups that have at least one AC submission."""
        groups_covered = []
        ac_languages = self.ac_languages()
        for language_group in language_groups:
            covered = False
            for language, count in ac_languages.items():
                if count > 0 and language_group.has_language(language):
                    covered = True
                    break
            if covered:
                groups_covered.append(language_group)
        return groups_covered
