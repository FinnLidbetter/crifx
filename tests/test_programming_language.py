"""Tests for the ProgrammingLanguage enumeration object."""

from crifx.contest_objects import ProgrammingLanguage


def test_guess_language():
    """Each recognized programming language is identified correctly."""
    cases = [
        ("sol.c", ProgrammingLanguage.C),
        ("sol.cc", ProgrammingLanguage.CPP),
        ("sol.cpp", ProgrammingLanguage.CPP),
        ("sol.py", ProgrammingLanguage.PYTHON),
        ("sol.java", ProgrammingLanguage.JAVA),
        ("sol.kt", ProgrammingLanguage.KOTLIN),
        ("sol.rs", ProgrammingLanguage.RUST),
        ("validator.ctd", ProgrammingLanguage.CTD),
        ("validator.viva", ProgrammingLanguage.VIVA),
        ("sol.bf", None),
        ("sol.extra_period.py", ProgrammingLanguage.PYTHON),
        ("path/to/file.java", ProgrammingLanguage.JAVA),
    ]
    # Languages are guessed from filenames as expected.
    for filename, expected in cases:
        assert ProgrammingLanguage.from_filename(filename) is expected
    # All languages are tested.
    languages_tested = set(language for _, language in cases if language is not None)
    assert len(languages_tested) == len(ProgrammingLanguage)
