#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState
from src.coordinates import square_to_coordinates, coordinates_to_square

# Initialize game state and validator
game_state = GameState()
validator = GameValidator(game_state)

# Test square validation
test_squares = ["e2", "e4", "ez", "z2", "e9", "12", "h8", "a1"]

for sq in test_squares:
    try:
        result = square_to_coordinates(sq)
        print(f"'{sq}' -> {result}")
    except Exception as e:
        print(f"'{sq}' -> Exception: {type(e).__name__}: {e}")

print()

# Test the parsing of "e2e4z" step by step
print("Parsing 'e2e4z':")
move_str = "e2e4z"
print(f"  Input: {move_str}")

# Check if it's a pawn move (no piece letter) or piece move
if move_str[0] in 'NBKRQ':  # Piece move (K=king, Q=queen, R=rook, B=bishop, N=knight)
    print(f"  Starts with piece letter: {move_str[0]}")
elif move_str[0] in 'abcdefgh' and len(move_str) >= 2 and move_str[1] == '=':
    print(f"  Pawn promotion format")
else:
    print(f"  Pawn move (starts with file letter '{move_str[0]}')")

# Look for 'x' indicating capture
if 'x' in move_str:
    print(f"  Contains capture indicator 'x'")
    move_str_no_x = move_str.replace('x', '')  # Remove for easier parsing
    print(f"  After removing 'x': {move_str_no_x}")
else:
    print(f"  No capture indicator")
    move_str_no_x = move_str

# Extract target square (last 2 characters should be like "e4", "f7", etc.)
# But need to account for promotion and check/checkmate symbols
target_start = None
for j in range(len(move_str_no_x) - 1, -1, -1):
    if j + 1 < len(move_str_no_x) and move_str_no_x[j] in 'abcdefgh' and move_str_no_x[j+1] in '12345678':
        target_start = j
        break

if target_start is None:
    print(f"  Could not find target square pattern")
else:
    target_square = move_str_no_x[target_start:target_start+2]
    print(f"  Target square: '{target_square}' (positions {target_start}-{target_start+1})")

    # Check if it's a valid square
    try:
        coord = square_to_coordinates(target_square)
        print(f"  Target square coordinates: {coord}")
    except Exception as e:
        print(f"  Target square '{target_square}' is invalid: {e}")