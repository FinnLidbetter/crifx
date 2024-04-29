"""Submission judgement enumeration object."""

from enum import Enum


class Judgement(Enum):
    """Classification of a submission."""

    ACCEPTED = "accepted"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    RUN_TIME_ERROR = "run_time_error"
    WRONG_ANSWER = "wrong_answer"

    def abbreviation(self) -> str:
        """Get a short form name for the judgement."""
        match self:
            case Judgement.ACCEPTED:
                return "AC"
            case Judgement.TIME_LIMIT_EXCEEDED:
                return "TLE"
            case Judgement.RUN_TIME_ERROR:
                return "RTE"
            case Judgement.WRONG_ANSWER:
                return "WA"
