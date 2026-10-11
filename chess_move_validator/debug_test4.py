#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState

# Initialize game state and validator
game_state = GameState()
validator = GameValidator(game_state)

# Replicate exactly what interactive_chess.py does
user_input = "e4"  # This is what the user entered
move_tokens = user_input.split()

print(f"User input: {repr(user_input)}")
print(f"Move tokens: {move_tokens}")

for token_index, move_token in enumerate(move_tokens):
    print(f"\nProcessing token {token_index}: {repr(move_token)}")

    # Skip empty tokens
    if not move_token.strip():
        print("  Skipping empty token")
        continue

    # Try to parse as algebraic notation using the validator's built-in method
    try:
        print("  Attempting algebraic notation parsing...")
        # Attempt to use the validator's parse_and_validate_algebraic_move method
        result = validator.parse_and_validate_algebraic_move(move_token)
        print(f"  Algebraic result: {result}")

        if result['accepted']:
            print(f"  + VALID MOVE: {move_token}")
            print(f"    Reason: {result['reason']}")
            # ... rest of success handling
        else:
            # Algebraic notation parsing succeeded but move was rejected
            print(f"  - INVALID MOVE: {move_token}")
            print(f"    Reason: {result['reason']}")
            # ... rest of rejection handling

    except Exception as e:
        print(f"  ! Exception in algebraic parsing: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

        # Fall back to coordinate parsing for backward compatibility
        print(f"  ? Attempting to parse '{move_token}' (coordinate fallback)...")

        # Try coordinate format first (e2e4)
        if len(move_token) == 4 and move_token[0] in 'abcdefgh' and move_token[1] in '12345678' and \
           move_token[2] in 'abcdefgh' and move_token[3] in '12345678':
            from_square = move_token[0:2]
            to_square = move_token[2:4]
            print(f"  Coordinate format detected: {from_square} -> {to_square}")

            result = validator.validate_move(from_square, to_square)

            if result['accepted']:
                print(f"  + VALID MOVE: {from_square}->{to_square}")
                print(f"    Reason: {result['reason']}")
                # ... rest of success handling
            else:
                print(f"  - INVALID MOVE: {from_square}->{to_square}")
                print(f"    Reason: {result['reason']}")
                # ... rest of rejection handling
        else:
            print(f"  Invalid format. Please use:")
            print(f"    - Algebraic notation: e4, Nf3, O-O, exd5, e8=Q")
            print(f"    - Coordinate format: e2e4, g1f3 (e.g., e2e4 for pawn from e2 to e4)")
            # ... rest of format error handling