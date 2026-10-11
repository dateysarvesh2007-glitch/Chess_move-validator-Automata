"""
Coordinate utilities for chess board positions.
Converts between algebraic notation (e.g., "e4") and row/column indices.
"""

def square_to_coordinates(square):
    """
    Convert algebraic notation to row, column indices.

    Args:
        square (str): Chess square in algebraic notation (e.g., "e4", "a1")

    Returns:
        tuple: (row, col) where row=0 is rank 1, col=0 is file 'a'

    Example:
        square_to_coordinates("e4") -> (3, 4)  # 4th row, 5th column (0-indexed)
        square_to_coordinates("a1") -> (0, 0)
        square_to_coordinates("h8") -> (7, 7)
    """
    if len(square) != 2:
        raise ValueError(f"Invalid square format: {square}. Expected format like 'e4'")

    file_char = square[0].lower()  # a-h
    rank_char = square[1]          # 1-8

    # Convert file (a-h) to column (0-7)
    if file_char < 'a' or file_char > 'h':
        raise ValueError(f"Invalid file: {file_char}. Must be between 'a' and 'h'")
    col = ord(file_char) - ord('a')

    # Convert rank (1-8) to row (0-7)
    # Note: In chess, rank 1 is at the bottom (row 0), rank 8 is at the top (row 7)
    try:
        rank = int(rank_char)
        if rank < 1 or rank > 8:
            raise ValueError(f"Invalid rank: {rank_char}. Must be between 1 and 8")
        row = rank - 1  # Convert to 0-indexed (rank 1 -> row 0)
    except ValueError:
        raise ValueError(f"Invalid rank: {rank_char}. Must be a digit between 1 and 8")

    return (row, col)


def coordinates_to_square(row, col):
    """
    Convert row, column indices to algebraic notation.

    Args:
        row (int): Row index (0-7, where 0 is rank 1)
        col (int): Column index (0-7, where 0 is file 'a')

    Returns:
        str: Chess square in algebraic notation (e.g., "e4", "a1")

    Example:
        coordinates_to_square(3, 4) -> "e4"
        coordinates_to_square(0, 0) -> "a1"
        coordinates_to_square(7, 7) -> "h8"
    """
    if not (0 <= row <= 7):
        raise ValueError(f"Row must be between 0 and 7, got {row}")
    if not (0 <= col <= 7):
        raise ValueError(f"Column must be between 0 and 7, got {col}")

    # Convert column to file (0->'a', 1->'b', ..., 7->'h')
    file_char = chr(ord('a') + col)

    # Convert row to rank (0->'1', 1->'2', ..., 7->'8')
    rank_char = str(row + 1)

    return f"{file_char}{rank_char}"


def is_valid_square(square):
    """
    Check if a string represents a valid chess square.

    Args:
        square (str): String to check

    Returns:
        bool: True if valid chess square notation, False otherwise
    """
    try:
        square_to_coordinates(square)
        return True
    except ValueError:
        return False


# Automata Theory Notes for Coordinates:
# This module provides a clean interface for converting between
# human-readable chess notation and internal representation.
# While not an automaton itself, it supports the DFA implementations
# in Layer 1 by providing standardized input/output format.