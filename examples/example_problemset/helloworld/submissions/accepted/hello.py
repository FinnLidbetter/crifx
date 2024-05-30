#!/bin/python3

"""Solution to the Hello World problem."""

# Use a crifx command to override the author for this submission instead
# of relying on git blame information.
# crifx!(author=Homer Simpson)

from sys import stdin

line = stdin.readline().strip()
print(f"Hello {line}")
