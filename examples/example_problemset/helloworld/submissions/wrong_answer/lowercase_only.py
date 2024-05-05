#!/bin/python3

"""This solution gives the wrong answer on cases that use uppercase letters."""

from sys import stdin

lower_line = stdin.readline().lower()

print(f"Hello {lower_line}")
