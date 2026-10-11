#!/usr/bin/env python3
"""
Demo script showing the interactive chess move validator in action.
This demonstrates how a user can play chess interactively with move validation.
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState


def main():
    """Demonstrate the interactive chess validator."""
    print("=" * 60)
    print("DEMO: Interactive Chess Move Validator")
    print("Four-Layer Automata Theory Architecture")
    print("=" * 60)
    print()

    # Initialize game state and validator
    game_state = GameState()
    validator = GameValidator(game_state)

    print("Starting position:")
    print(game_state.board.display())
    print(f"Current turn: {game_state.current_turn}")
    print()

    # Demonstrate a few moves
    moves_to_try = [
        ("e2", "e4", "White pawn e2-e4"),
        ("e7", "e5", "Black pawn e7-e5"),
        ("g1", "f3", "White knight g1-f3"),
        ("b8", "c6", "Black knight b8-c6"),
        ("f1", "b5", "White bishop f1-b5"),
    ]

    for i, (from_sq, to_sq, description) in enumerate(moves_to_try, 1):
        print(f"Move {i}: {description}")
        print(f"Attempting: {from_sq} -> {to_sq}")

        # Validate the move
        result = validator.validate_move(from_sq, to_sq)

        if result['accepted']:
            print(f" ACCEPTED: {result['reason']}")

            # Apply the move
            game_state.make_move(from_sq, to_sq)

            print(f"Board after move:")
            print(game_state.board.display())
            print(f"Current turn: {game_state.current_turn}")
            print()
        else:
            print(f" REJECTED: {result['reason']}")
            print()
            break

    print("Move history:")
    for i, move in enumerate(game_state.move_history, 1):
        print(f"  {i}. {move['from']} -> {move['to']} ({move['piece']})")

    print()
    print("=" * 60)
    print("DEMO COMPLETE")
    print("The interactive_chess.py script provides full interactive play.")
    print("=" * 60)


if __name__ == "__main__":
    main()