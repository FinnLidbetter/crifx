#!/bin/python3

"""Loop forever, then print the first line of input."""

from sys import stdin

val = 0
while True:
    val = 1 - val
    if val == 2:
        break

line = stdin.readline()
print(line)
