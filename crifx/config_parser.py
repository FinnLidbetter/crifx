"""
Configuration parsing for defining problem review requirements.

The configuration file is also used for manually tracking the review status
of the different parts of each problem.
"""

import logging
import os
import tomllib
from dataclasses import dataclass
from typing import Any

from crifx.contest_objects import LanguageGroup, ProgrammingLanguage

CONFIG_FILENAME = "crifx.toml"


def _get_or_default(key: str, dct: dict[str, Any], obj: Any) -> Any:
    """Get a value from a dictionary or from a fallback object."""
    if key in dct:
        return dct.get(key)
    return getattr(obj, key)


@dataclass(frozen=True)
class ReviewCountRequirements:
    """Requirements applicable to each problem."""

    # The number of distinct judges required to have provided an AC submission.
    independent_ac: int
    # The number of language groups required to have an AC submission.
    language_groups_ac: int
    # The number of wrong_answer submissions required.
    submissions_wa: int
    # The number of tle submissions required.
    submissions_tle: int
    # The number of judges required to have reviewed the problem statement.
    statement_reviewers: int
    # The number of judges required to have reviewed the input validator(s).
    validator_reviewers: int
    # The number of judges required to have reviewed the test data.
    data_reviewers: int

    @staticmethod
    def from_toml_dict(toml_dict: dict[str, int]) -> "ReviewCountRequirements":
        """Initialize ReviewCountRequirements from a toml dict."""
        return ReviewCountRequirements(
            _get_or_default("independent_ac", toml_dict, REVIEW_COUNT_DEFAULT),
            _get_or_default("language_groups_ac", toml_dict, REVIEW_COUNT_DEFAULT),
            _get_or_default("submissions_wa", toml_dict, REVIEW_COUNT_DEFAULT),
            _get_or_default("submissions_tle", toml_dict, REVIEW_COUNT_DEFAULT),
            _get_or_default("statement_reviewers", toml_dict, REVIEW_COUNT_DEFAULT),
            _get_or_default("validator_reviewers", toml_dict, REVIEW_COUNT_DEFAULT),
            _get_or_default("data_reviewers", toml_dict, REVIEW_COUNT_DEFAULT),
        )


REVIEW_COUNT_DEFAULT = ReviewCountRequirements(
    independent_ac=3,
    language_groups_ac=2,
    submissions_wa=1,
    submissions_tle=1,
    statement_reviewers=3,
    validator_reviewers=2,
    data_reviewers=2,
)


@dataclass(frozen=True)
class LanguageGroupConfig:
    """Configuration for requirements for a language group."""

    # Identifier name used for the language group.
    identifier: str
    # The programming languages in the group.
    language_group: LanguageGroup
    # The number of required AC submissions from this group.
    required_ac_count: int = 0

    @staticmethod
    def from_toml_dict(
        toml_dict: dict[str, Any], group_identifier: str
    ) -> "LanguageGroupConfig":
        """Initialize a LanguageGroupConfig from a toml dict."""
        language_names = toml_dict.get("languages", [])
        languages = []
        for language_name in language_names:
            language = ProgrammingLanguage.from_language_name(language_name)
            if language is None:
                logging.warning(
                    "Language %s is not recognized by crifx.", language_name
                )
            else:
                languages.append(language)
        return LanguageGroupConfig(
            identifier=group_identifier,
            language_group=LanguageGroup(*languages),
            required_ac_count=toml_dict.get("required_ac_count", 0),
        )


@dataclass(frozen=True)
class ProblemReviewStatus:
    """Metadata for tracking who has reviewed different parts of a problem."""

    # A list of names of judges who have reviewed the problem statement.
    statement_reviewed_by: list[str]
    # A list of names of judges who have reviewed the input validator(s).
    validators_reviewed_by: list[str]
    # A list of names of judges who have reviewed the test data.
    data_reviewed_by: list[str]

    @staticmethod
    def from_toml_dict(toml_dict: dict[str, Any]) -> "ProblemReviewStatus":
        """Create a ProblemReviewStatus from a toml configuration dict."""
        return ProblemReviewStatus(
            statement_reviewed_by=toml_dict.get("statement_reviewed_by", []),
            validators_reviewed_by=toml_dict.get("validators_reviewed_by", []),
            data_reviewed_by=toml_dict.get("data_reviewed_by", []),
        )


@dataclass(frozen=True)
class ProblemConfig:
    """Configuration data for a problem in a problem set."""

    # The name of the problem.
    name: str
    # The github issue id associated with the problem.
    github_issue_id: int | None
    # Tracking information about who has reviewed different parts of the problem.
    review_status: ProblemReviewStatus

    @staticmethod
    def from_toml_dict(toml_dict: dict[str, Any], problem_name: str):
        """Create a ProblemConfig from a toml dict."""
        return ProblemConfig(
            name=problem_name,
            github_issue_id=toml_dict.get("github_issue_id"),
            review_status=ProblemReviewStatus.from_toml_dict(
                toml_dict.get("review_status", {})
            ),
        )


class Config:
    """Configuration for crifx requirements and review status."""

    def __init__(self, toml_dict):
        self.github_repo_url = toml_dict.get("github_repo_url")
        self.review_requirements = ReviewCountRequirements.from_toml_dict(
            toml_dict.get("review_requirements", {}),
        )
        self.language_group_configs = []
        language_groups = toml_dict.get("language_groups", {})
        for group_identifier, language_group_dict in language_groups.items():
            language_group_config = LanguageGroupConfig.from_toml_dict(
                language_group_dict, group_identifier
            )
            if not language_group_config.language_group.languages:
                # No languages parsed from the language group.
                continue
            self.language_group_configs.append(language_group_config)
        self.problem_configs = []
        problems = toml_dict.get("problems", {})
        for problem_name, problem_dict in problems.items():
            problem_review_status = ProblemConfig.from_toml_dict(
                problem_dict, problem_name
            )
            self.problem_configs.append(problem_review_status)
        self.problem_configs.sort(key=lambda x: x.name)


def parse_config(problemset_root_path: str) -> Config:
    """Parse a configuration file into a Config object."""
    config_path = os.path.join(problemset_root_path, CONFIG_FILENAME)
    with open(config_path, "rb") as config_file:
        toml_dict = tomllib.load(config_file)
    return Config(toml_dict)
