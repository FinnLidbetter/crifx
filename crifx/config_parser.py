"""
Configuration parsing for defining problem review requirements.

The configuration file is also used for manually tracking the review status
of the different parts of each problem.
"""

import itertools
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
    def from_toml_dict(toml_dict: dict[str, Any]) -> "LanguageGroupConfig":
        """Initialize a LanguageGroupConfig from a toml dict."""
        group_identifier = toml_dict.get("name")
        if group_identifier is None:
            raise ValueError(
                "Language group in the `crifx.toml` file is missing a 'name'"
            )
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
class AliasGroup:
    """Alias group object for parsing alternate names from a config file."""

    identifier: str
    git_name: str | None
    aliases: list[str]

    @staticmethod
    def from_toml_dict(toml_dict: dict[str, Any]) -> "AliasGroup":
        """Parse an AliasGroup from a toml dictionary."""
        primary_name = toml_dict.get("primary_name")
        if primary_name is None:
            raise ValueError(
                "The `crifx.toml` file is missing a 'primary_name' for one or more 'judge' tables."
            )
        git_name = toml_dict.get("git_name")
        aliases = toml_dict.get("aliases", [])
        return AliasGroup(primary_name, git_name, aliases)


class Config:
    """Configuration for crifx requirements and review status."""

    def __init__(self, toml_dict):
        self.github_repo_url = toml_dict.get("github_repo_url")
        self.review_requirements = ReviewCountRequirements.from_toml_dict(
            toml_dict.get("review_requirements", {}),
        )
        self.language_group_configs = []
        self.alias_groups = []
        language_groups = toml_dict.get("language_group", [])
        for language_group_dict in language_groups:
            language_group_config = LanguageGroupConfig.from_toml_dict(
                language_group_dict,
            )
            if not language_group_config.language_group.languages:
                # No languages parsed from the language group.
                continue
            self.language_group_configs.append(language_group_config)
        alias_groups = toml_dict.get("judge", [])
        for alias_group_dict in alias_groups:
            alias_group = AliasGroup.from_toml_dict(alias_group_dict)
            self.alias_groups.append(alias_group)
        for alias_group_1, alias_group_2 in itertools.product(
            self.alias_groups, self.alias_groups
        ):
            if alias_group_1 == alias_group_2:
                continue
            shared_aliases = list(
                set(alias_group_1.aliases) & set(alias_group_2.aliases)
            )
            if shared_aliases:
                logging.warning(
                    "Judges '%s' and '%s' share the following aliases: %s. Remove shared "
                    "aliases from the crifx configuration file.",
                    alias_group_1.identifier,
                    alias_group_2.identifier,
                )

    @property
    def track_review_status(self) -> bool:
        """Return True iff manual reviews are required to be tracked in files per problem."""
        return (
            self.review_requirements.statement_reviewers > 0
            or self.review_requirements.data_reviewers > 0
            or self.review_requirements.validator_reviewers > 0
        )


def parse_config(problemset_root_path: str) -> Config:
    """Parse a configuration file into a Config object."""
    config_path = os.path.join(problemset_root_path, CONFIG_FILENAME)
    with open(config_path, "rb") as config_file:
        toml_dict = tomllib.load(config_file)
    return Config(toml_dict)
