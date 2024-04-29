"""Logic for interacting with git."""

import os
from collections import defaultdict
from dataclasses import dataclass

from pygit2 import Repository, Signature, discover_repository
from pygit2.enums import BlameFlag, SortMode


@dataclass(frozen=True)
class GitUser:
    """Data structure for git user information."""

    name: str
    email: str
    raw_name: bytes
    raw_email: bytes

    @staticmethod
    def from_signature(signature: Signature) -> "GitUser":
        """Create a GitUser object from a pygit2 Signature."""
        return GitUser(
            signature.name, signature.email, signature.raw_name, signature.raw_email
        )


class GitManager:
    """Manager class for interacting with git."""

    def __init__(self, path_in_repo: str):
        repo_path = discover_repository(path_in_repo)
        if repo_path is None:
            raise ValueError(f"Path '{path_in_repo}' is not in a git repository.")
        self.repo = Repository(repo_path)

    def get_committers_and_authors(self) -> list[GitUser]:
        """Get a list of every git user that has authored or committed a commit."""
        last_commit = self.repo[self.repo.head.target]
        git_users = set()
        for commit in self.repo.walk(last_commit.id, SortMode.TIME):
            author = commit.author
            committer = commit.committer
            git_users.add(GitUser.from_signature(author))
            git_users.add(GitUser.from_signature(committer))
        return sorted(git_users, key=lambda x: x.name)

    def guess_file_author(self, path: str) -> GitUser | None:
        """Guess the author of a file path."""
        if not os.path.isfile(path):
            raise ValueError(f"Path '{path}' is not a file.")
        blame = self.repo.blame(
            path, flags=BlameFlag.NORMAL | BlameFlag.IGNORE_WHITESPACE
        )
        lines_modified: defaultdict[GitUser, int] = defaultdict(int)
        lines_max = 0
        user_max = None
        for hunk in blame:
            committer = hunk.final_committer
            git_user = GitUser.from_signature(committer)
            lines_modified[git_user] += hunk.lines_in_hunk
            if lines_modified[git_user] > lines_max:
                lines_max = lines_modified[git_user]
                user_max = git_user
        return user_max
