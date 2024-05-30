"""Object for representing a submission author."""

from crifx.git_manager import GitUser


class Judge:
    """Object for representing a judge submission author."""

    def __init__(self, primary_name: str, git_user: GitUser | None, *aliases: str):
        self.primary_name: str = primary_name
        self.git_name: str | None = getattr(git_user, "name", None)
        name_set = {name for name in aliases}
        name_set.add(primary_name)
        if self.git_name is not None:
            name_set.add(self.git_name)
        self.aliases = [name.lower() for name in name_set]

    def has_alias(self, name: str):
        """Determine if the provided name corresponds to this judge."""
        return name.lower() in self.aliases

    def is_same(self, other_judge):
        """Determine if two Judge objects correspond to the same person."""
        return (
            self.git_name == other_judge.git_name
            or self.primary_name == other_judge.primary_name
        )

    def __str__(self):
        return f"{self.primary_name}"


UNKNOWN_JUDGE = Judge("UNKNOWN", None)
