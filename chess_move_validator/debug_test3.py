#!/usr/bin/env python3

# Test how split() works
test_strings = [
    "e4",
    " e4",
    "e4 ",
    " e4 ",
    "e4	e5",  # tab
    "e4	e5 ",  # tab and space
    " e4 e5 ",
    "",
    "   ",
    "e4  e5",  # multiple spaces
]

for s in test_strings:
    tokens = s.split()
    print(f"Input: {repr(s)}")
    print(f"  Split tokens: {tokens}")
    print()