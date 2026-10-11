#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState

# Initialize game state and validator
game_state = GameState()
validator = GameValidator(game_state)

# Test with various inputs that might have whitespace
test_inputs = ['e4', ' e4', 'e4 ', ' e4 ', 'e4\t', '\te4', '\te4\t']

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