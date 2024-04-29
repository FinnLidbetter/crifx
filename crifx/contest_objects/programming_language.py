"""Programming language enumeration object."""

from enum import Enum


class ProgrammingLanguage(Enum):
    """Recognised programming languages."""

    C = "C"
    CPP = "C++"
    PYTHON = "Python"
    JAVA = "Java"
    KOTLIN = "Kotlin"
    RUST = "Rust"
    CTD = "Checktestdata"
    VIVA = "Viva"

    def file_extensions(self) -> list[str]:
        """Get a list of recognised file extensions for the language."""
        match self:
            case ProgrammingLanguage.C:
                return ["c"]
            case ProgrammingLanguage.CPP:
                return ["cc", "cpp"]
            case ProgrammingLanguage.PYTHON:
                return ["py"]
            case ProgrammingLanguage.JAVA:
                return ["java"]
            case ProgrammingLanguage.KOTLIN:
                return ["kt"]
            case ProgrammingLanguage.RUST:
                return ["rs"]
            case ProgrammingLanguage.CTD:
                return ["ctd"]
            case ProgrammingLanguage.VIVA:
                return ["viva"]


def guess_programming_language(filename: str) -> ProgrammingLanguage | None:
    """Guess the programming language from a file name."""
    extension = filename[filename.rindex(".") + 1 :]
    for programming_language_str in ProgrammingLanguage:
        programming_language = ProgrammingLanguage(programming_language_str)
        if extension in programming_language.file_extensions():
            return programming_language
    return None


class LanguageGroup:
    """A group of programming languages."""

    def __init__(self, *languages: ProgrammingLanguage):
        self.languages = tuple(sorted(languages, key=lambda x: x.value))
