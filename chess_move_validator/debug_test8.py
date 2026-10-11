#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState

# Initialize game state and validator
game_state = GameState()
validator = GameValidator(game_state)

# Test inputs that should cause exceptions in algebraic parsing
test_inputs = [
    "",           # Empty string
    "=",          # Just equals
    "e=",         # File and equals but no target
    "ex",         # File and x but no target
    "ex=",        # File, x, equals but no target
    "e2=",        # File, rank, equals but no promotion piece
    "e2=z",       # File, rank, equals but invalid promotion piece
    "e2e4e2e4",   # Too long - might confuse the parser
    "@#$%",       # Completely invalid characters
]

for test_input in test_inputs:
    print(f"Testing parse_and_validate_algebraic_move('{repr(test_input)}')...")
    try:
        result = validator.parse_and_validate_algebraic_move(test_input)
        print(f"  Result: {result}")
        if result['accepted']:
            print("  Move was accepted!")
        else:
            print(f"  Move was rejected: {result['reason']}")
    except Exception as e:
        print(f"  Exception thrown: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    print()