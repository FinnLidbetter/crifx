"""Tests for methods on the Problem object."""

from crifx.contest_objects import Judgement, Problem, ProgrammingLanguage
from crifx.report_objects import DEFAULT_REVIEW_STATUS


def test_language_count(make_judged_lang_submission):
    """Test counting the number of submissions for each language."""
    ac_java_1 = make_judged_lang_submission(
        Judgement.ACCEPTED,
        ProgrammingLanguage.JAVA,
    )
    ac_java_2 = make_judged_lang_submission(
        Judgement.ACCEPTED, ProgrammingLanguage.JAVA
    )
    ac_c = make_judged_lang_submission(Judgement.ACCEPTED, ProgrammingLanguage.C)
    wa_java = make_judged_lang_submission(
        Judgement.WRONG_ANSWER, ProgrammingLanguage.JAVA
    )
    tle_kotlin = make_judged_lang_submission(
        Judgement.TIME_LIMIT_EXCEEDED, ProgrammingLanguage.KOTLIN
    )
    rte_rust = make_judged_lang_submission(
        Judgement.RUN_TIME_ERROR, ProgrammingLanguage.RUST
    )
    problem = Problem(
        "problem",
        [],
        [ac_java_1, tle_kotlin, wa_java, rte_rust, ac_c, ac_java_2],
        DEFAULT_REVIEW_STATUS,
    )
    ac_languages = problem.ac_languages()
    assert ac_languages == {ProgrammingLanguage.JAVA: 2, ProgrammingLanguage.C: 1}
    assert sorted(problem.ac_submissions, key=lambda x: x.language.value) == [
        ac_c,
        ac_java_1,
        ac_java_2,
    ]
    assert problem.wa_submissions == [wa_java]
    assert problem.tle_submissions == [tle_kotlin]
    assert problem.rte_submissions == [rte_rust]
    problem = Problem("problem", [], [], DEFAULT_REVIEW_STATUS)
    ac_languages = problem.ac_languages()
    assert ac_languages == {}
    assert problem.ac_submissions == []
    assert problem.wa_submissions == []
    assert problem.tle_submissions == []
    assert problem.rte_submissions == []


def test_independent_author_count(make_authored_submission):
    """Test counting the number of submissions from distinct judges."""
    finn_java_ac_1 = make_authored_submission(
        "Finn", None, Judgement.ACCEPTED, ProgrammingLanguage.JAVA
    )
    finn_java_ac_2 = make_authored_submission(
        "Finn", None, Judgement.ACCEPTED, ProgrammingLanguage.JAVA
    )
    finn_rust_ac = make_authored_submission(
        "Finn", None, Judgement.ACCEPTED, ProgrammingLanguage.RUST
    )
    alice_c_ac = make_authored_submission(
        "Alice", "alice", Judgement.ACCEPTED, ProgrammingLanguage.C
    )
    alice_c_wa = make_authored_submission(
        "Alice", "alice", Judgement.WRONG_ANSWER, ProgrammingLanguage.C
    )
    bob_java_tle = make_authored_submission(
        "Bob", "bob", Judgement.TIME_LIMIT_EXCEEDED, ProgrammingLanguage.JAVA
    )
    problem = Problem(
        "problem", [], [finn_java_ac_1, alice_c_ac, bob_java_tle], DEFAULT_REVIEW_STATUS
    )
    assert problem.independent_ac_count() == 2
    problem = Problem(
        "problem", [], [finn_java_ac_1, finn_rust_ac], DEFAULT_REVIEW_STATUS
    )
    assert problem.independent_ac_count() == 1
    problem = Problem("problem", [], [alice_c_wa, bob_java_tle], DEFAULT_REVIEW_STATUS)
    assert problem.independent_ac_count() == 0
    problem = Problem(
        "problem",
        [],
        [finn_java_ac_1, finn_java_ac_2, bob_java_tle],
        DEFAULT_REVIEW_STATUS,
    )
    assert problem.independent_ac_count() == 1
