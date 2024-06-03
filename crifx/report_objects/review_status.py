"""ReviewStatus object for tracking information about a problem."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewStatus:
    """Per-problem status tracking data."""

    github_issue_id: int | None
    statement_reviewed_by: list[str]
    validators_reviewed_by: list[str]
    data_reviewed_by: list[str]


DEFAULT_REVIEW_STATUS = ReviewStatus(None, [], [], [])


DEFAULT_REVIEW_STATUS_TOML = """
# The GitHub Issue id for the problem, if there is one.
# github_issue_id = 

[review_status]
# Add your name in double quotes on a new line in this list if you have read
# the problem statement and believe that no further changes are necessary to
# the problem statement.
statement_reviewed_by = [

]
# Add your name in double quotes on a new line in this list if you have 
# reviewed the input validators and compared them to the problem statement and
# you believe that no further changes are necessary and all guarantees in the
# problem statement about the input are verified by an input validator.
validators_reviewed_by = [

]
# Add your name in double quotes on a new line in this list if you have 
# reviewed the test data and you believe that no further data is necessary to 
# ensure that incorrect solutions will be judged as WRONG ANSWER, too slow 
# solutions will be judged as TIME_LIMIT_EXCEEDED, and correct solutions will
# be judged as ACCEPTED.
data_reviewed_by = [

]
"""
