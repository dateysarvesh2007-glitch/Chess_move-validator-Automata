#!/usr/bin/env python3
"""
Chess Move Legality Checker
A Theory of Computation project demonstrating chess move validation
using automata theory concepts (DFA, FSM, and layered validation).
"""

from src.layer3.game_validator import GameValidator
from src.game_state import GameState


def main():
    """Main demonstration of the chess move legality checker."""
    print("=" * 60)
    print("Chess Move Legality Checker")
    print("A Theory of Computation Project")
    print("=" * 60)
    print()

    # Initialize game state with standard starting position
    game_state = GameState()
    validator = GameValidator(game_state)

    # Example demonstrations
    examples = [
        (('e2', 'e4'), "Legal two-square pawn advance"),
        (('e2', 'e5'), "Illegal - pawn cannot move three squares"),
        (('g1', 'f3'), "Legal knight move"),
        (('g1', 'h4'), "Illegal - knight cannot move that way"),
        (('b1', 'c3'), "Legal knight move"),
        (('f1', 'b5'), "Illegal - bishop blocked by pawn"),
        (('e1', 'e2'), "Illegal - king cannot move to occupied square"),
        (('e1', 'e3'), "Illegal - king cannot move two squares normally"),
    ]

    print("Individual Move Examples:")
    print("-" * 40)

    for i, ((from_sq, to_sq), description) in enumerate(examples, 1):
        print(f"{i}. {description}")
        print(f"   Move: {from_sq} -> {to_sq}")

        # Validate the move
        result = validator.validate_move(from_sq, to_sq)

        if result['accepted']:
            print(f"   Result: ACCEPT")
            if result.get('is_check'):
                print(f"   Output: {result['move_notation']}+")
            else:
                print(f"   Output: {result['move_notation']}")
            print(f"   Reason: {result['reason']}")
        else:
            print(f"   Result: REJECT")
            print(f"   Reason: {result['reason']}")

        print()

    # Demonstrate a short game sequence
    print("Short Game Sequence:")
    print("-" * 40)

    # Reset for clean sequence
    game_state = GameState()
    validator = GameValidator(game_state)

    sequence = [
        ('e2', 'e4', 'White controls center'),
        ('e7', 'e5', 'Black mirrors'),
        ('g1', 'f3', 'White knight develops'),
        ('f8', 'c5', 'Black bishop challenges center'),
        ('f1', 'c4', 'White bishop targets weak point'),
        ('d7', 'd6', 'Black defends'),
    ]

    for i, (from_sq, to_sq, description) in enumerate(sequence, 1):
        print(f"{i}. {description}: {from_sq} -> {to_sq}")

        # Validate the move
        result = validator.validate_move(from_sq, to_sq)

        if result['accepted']:
            print(f"   Result: ACCEPT")
            if result.get('is_check'):
                print(f"   Output: {result['move_notation']}+ (Check!)")
            else:
                print(f"   Output: {result['move_notation']}")
            print(f"   Reason: {result['reason']}")

            # Apply the move to update the game state
            game_state.make_move(from_sq, to_sq)
        else:
            print(f"   Result: REJECT")
            print(f"   Reason: {result['reason']}")
            print("   Sequence terminated due to illegal move.")
            break

        print()

    # Show final position
    print("Final Position:")
    print("-" * 40)
    print(game_state.board.display())
    print()

    # Show move history
    print("Move History:")
    print("-" * 40)
    for i, move in enumerate(game_state.move_history, 1):
        print(f"{i}. {move['from']} -> {move['to']} ({move['piece']})")

    print()
    print("=" * 60)
    print("Demonstration Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()