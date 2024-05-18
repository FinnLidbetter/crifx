"""Programming language enumeration object."""

from enum import Enum
from typing import Union


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
                return ["cc", "cpp", "cxx", "C"]
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

    @staticmethod
    def from_filename(filename: str) -> Union["ProgrammingLanguage", None]:
        """Guess the programming language from a file name."""
        if "." not in filename:
            return None
        extension = filename[filename.rindex(".") + 1 :]
        for programming_language_str in ProgrammingLanguage:
            programming_language = ProgrammingLanguage(programming_language_str)
            if extension in programming_language.file_extensions():
                return programming_language
        return None

    @staticmethod
    def from_language_name(language_name: str) -> Union["ProgrammingLanguage", None]:
        """Get the programming language from a language name string."""
        for programming_language in ProgrammingLanguage:
            if language_name.lower() == programming_language.value.lower():
                return programming_language
        return None


class LanguageGroup:
    """A group of programming languages."""

    def __init__(self, *languages: ProgrammingLanguage):
        self.languages = tuple(sorted(languages, key=lambda x: x.value))

    def has_language(self, language: ProgrammingLanguage) -> bool:
        """Return True if the given language is in the group."""
        return language in self.languages

    def __eq__(self, other):
        if not isinstance(other, LanguageGroup):
            return False
        return self.languages == other.languages

    def __hash__(self):
        return hash(self.languages)
