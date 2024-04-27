"""Module for detecting and parsing the problem and contest directory structure."""

import os

PROBLEM_ROOT_INDICATOR_DIRS = [
    "submissions",
    "problem_statement",
]

PROBLEM_ROOT_INDICATOR_FILES = [
    "problem.yaml",
    "problem.yml",
]


def is_problem_root_dir(path: str) -> bool:
    """Detect if the given path is the root of a problem directory."""
    if not os.path.isdir(path):
        return False
    for dir_obj_name in os.listdir(path):
        dir_obj_path = os.path.join(path, dir_obj_name)
        if os.path.isdir(dir_obj_path) and dir_obj_name in PROBLEM_ROOT_INDICATOR_DIRS:
            return True
        if (
            os.path.isfile(dir_obj_path)
            and dir_obj_name in PROBLEM_ROOT_INDICATOR_FILES
        ):
            return True
    return False


def get_problem_root_dirs(path: str) -> list[str]:
    """Get the problem root directory paths under the current directory."""
    if not os.path.isdir(path):
        return []
    problem_root_dirs = []
    try:
        for dir_obj_name in os.listdir(path):
            dir_obj_path = os.path.join(path, dir_obj_name)
            if os.path.isdir(dir_obj_path) and is_problem_root_dir(dir_obj_path):
                problem_root_dirs.append(dir_obj_path)
        return problem_root_dirs
    except PermissionError:
        return []


def is_contest_problems_root(path: str) -> bool:
    """Detect if a path has one or more problem root directories."""
    return bool(get_problem_root_dirs(path))


def find_contest_problems_root() -> str | None:
    """
    Find the contest problems directory path from the current working directory.

    Return `None` if the directory is not found within 5 parent levels.
    """
    current_dir = os.getcwd()
    candidate_dir = current_dir
    parents_max = 5
    for _ in range(parents_max):
        if is_contest_problems_root(candidate_dir):
            return candidate_dir
        candidate_dir = os.path.dirname(candidate_dir)
    return None
