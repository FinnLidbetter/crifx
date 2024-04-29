"""Object for representing a submission author."""


class Author:
    """Object for representing a submission author."""

    def __init__(self, primary_name, git_name=None, *aliases):
        self.primary_name = primary_name
        self.git_name = git_name
        name_set = {name for name in aliases}
        name_set.add(primary_name)
        if git_name is not None:
            name_set.add(git_name)
        self.aliases = list(name_set)

    def has_alias(self, name):
        """Determine if the provided name corresponds to this author."""
        return name in self.aliases

    def is_same(self, other_author):
        """Determine if two Author objects correspond to the same person."""
        return (
            self.git_name == other_author.git_name
            or self.primary_name == other_author.git_name
        )
