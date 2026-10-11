#!/usr/bin/env python3
"""
Process a specific chess move sequence through the validator.
This demonstrates how the four-layer automata theory architecture
validates a complete game sequence.
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState


def main():
    """Process the provided move sequence."""
    print("=" * 70)
    print("PROCESSING CHESS MOVE SEQUENCE THROUGH FOUR-LAYER VALIDATOR")
    print("=" * 70)
    print()

    # Initialize game state and validator
    game_state = GameState()
    validator = GameValidator(game_state)

    # The move sequence provided by the user
    move_sequence = [
        "e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4", "Bxb4", "c3", "Ba5",
        "d4", "exd4", "O-O", "dxc3", "Qb3", "Qf6", "e5", "Qg6", "Nxc3", "Nge7",
        "Nd5", "Nxd5", "Bxd5", "O-O", "Ba3", "Re8", "Rad1", "Bb6", "Rfe1", "Na5",
        "Qc3", "c6", "Be4", "Qh6", "Bc1", "Qe6", "Ng5", "Qc4", "Qh3", "h6",
        "Bh7+", "Kf8", "Re4", "Qxa2", "Bf5", "Qxf2+", "Kh1", "hxg5", "Bxg5", "d5", "Qh8#"
    ]

    print("Starting Position:")
    print(game_state.board.display())
    print(f"Current turn: {game_state.current_turn}")
    print()

    # Process each move
    for i, move_str in enumerate(move_sequence, 1):
        # Determine whose turn it is
        current_turn = game_state.current_turn

        print(f"Move {i} ({current_turn}): {move_str}")

        # Parse and validate the move (this also applies it if valid)
        try:
            result = validator.parse_and_validate_algebraic_move(move_str)

            if result['accepted']:
                print("  ACCEPTED: {}".format(result['reason']))

                # Show if it's check or checkmate
                if result.get('is_check'):
                    if '#' in move_str:
                        print("  CHECKMATE! {}".format(move_str))
                    else:
                        print("  CHECK: {}+".format(move_str))
                else:
                    print("  MOVE: {}".format(move_str))

                print("  REASON: {}".format(result['reason']))

            else:
                print("  REJECTED: {}".format(result['reason']))
                print("  SEQUENCE TERMINATED AT MOVE {}".format(i))
                break

        except Exception as e:
            print("  ERROR processing move: {}".format(e))
            print("  SEQUENCE TERMINATED AT MOVE {}".format(i))
            break

        # Show board position after move
        print("  BOARD AFTER MOVE {}:".format(i))
        print(game_state.board.display())
        print("  TURN NOW: {}".format(game_state.current_turn))
        print()

        # Small delay for readability (in real terminal, you might want to press enter to continue)
        # For now, we'll just continue

    # Final position
    print("=" * 70)
    print("FINAL POSITION")
    print("=" * 70)
    print(game_state.board.display())
    print()

    # Move history
    print("MOVE HISTORY:")
    print("-" * 30)
    for i, move in enumerate(game_state.move_history, 1):
        print("{:2d}. {} -> {} ({})".format(i, move['from'], move['to'], move['piece']))

    print()
    print("Total moves processed: {}".format(len(game_state.move_history)))
    print("Game state: {} to move".format('White' if game_state.current_turn == 'white' else 'Black'))

    # Check if last move was checkmate
    if len(move_sequence) > 0:
        last_move = move_sequence[-1]
        if '#' in last_move:
            print("CHECKMATE! Last move delivers checkmate! Game over.")
        elif '+' in last_move:
            print("CHECK: Last move delivers check.")

    print("=" * 70)


if __name__ == "__main__":
    main()