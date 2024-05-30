#!/bin/python3

"""
This file uses 'jd' in the filename.

This is an alias defined for Jane Doe in the crifx.toml file.
"""

from sys import stdin

tokens = stdin.readline().split(" ")
print(int(tokens[0]) + int(tokens[1]))
