#!/usr/bin/env python3
"""
Interactive Chess Move Validator
Allows users to input chess moves manually and see board visualization
with move validation using the four-layer automata theory architecture.
"""

import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState


def print_welcome():
    """Print welcome message and instructions."""
    print("=" * 60)
    print("INTERACTIVE CHESS MOVE VALIDATOR")
    print("Four-Layer Automata Theory Architecture")
    print("=" * 60)
    print()
    print("Instructions:")
    print("- Enter moves in standard algebraic notation (e.g., e4, Nf3, O-O, exd5)")
    print("- Type 'quit' or 'exit' to stop the game")
    print("- Type 'board' to see the current board state")
    print("- Type 'reset' to start a new game")
    print("- Type 'history' to see move history")
    print("- Type 'help' to show these instructions again")
    print()
    print("Layer Information:")
    print("- Layer 1: Piece-specific DFAs (basic movement validation)")
    print("- Layer 2: History-dependent FSMs (castling, en passant)")
    print("- Layer 3: Game sequence validator (turn management, coordination)")
    print("- Layer 4: Safety filter (king safety/check detection)")
    print()


def print_board(game_state):
    """Display the current board state."""
    print("\nCurrent Board Position:")
    print("-" * 30)
    print(game_state.board.display())
    print(f"\nCurrent turn: {game_state.current_turn}")
    print()


def print_move_history(game_state):
    """Display the move history."""
    print("\nMove History:")
    print("-" * 20)
    if not game_state.move_history:
        print("No moves made yet")
    else:
        for i, move in enumerate(game_state.move_history, 1):
            print(f"{i:2d}. {move['from']} -> {move['to']} ({move['piece']})")
    print()


def main():
    """Main interactive chess game loop."""
    # Initialize game state and validator
    game_state = GameState()
    validator = GameValidator(game_state)

    print_welcome()
    print_board(game_state)

    move_number = 1

    while True:
        try:
            # Get user input
            user_input = input(f"Move {move_number} ({game_state.current_turn}): ").strip()

            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("Thanks for playing!")
                break
            elif user_input.lower() == 'board':
                print_board(game_state)
                continue
            elif user_input.lower() == 'reset':
                game_state = GameState()
                validator = GameValidator(game_state)
                move_number = 1
                print("Game reset. Starting position:")
                print_board(game_state)
                continue
            elif user_input.lower() == 'history':
                print_move_history(game_state)
                continue
            elif user_input.lower() == 'help':
                print_welcome()
                print_board(game_state)
                continue
            elif user_input.lower() == '':
                # Empty input, just show board again
                print_board(game_state)
                continue

            # Split input by whitespace to handle multiple moves per line
            move_tokens = user_input.split()

            # Process each move token in sequence
            for token_index, move_token in enumerate(move_tokens):
                # Skip empty tokens
                if not move_token.strip():
                    continue

                # Try to parse as algebraic notation using the validator's built-in method
                try:
                    # Attempt to use the validator's parse_and_validate_algebraic_move method
                    result = validator.parse_and_validate_algebraic_move(move_token)

                    if result['accepted']:
                        print(f"\n+ VALID MOVE: {move_token}")
                        print(f"  Reason: {result['reason']}")

                        # Show if it's check (the move has already been applied by the validator)
                        if result.get('is_check'):
                            print(f"  {move_token}+ (Check!)")

                        print_board(game_state)
                        move_number += 1

                        # Check for game over conditions (simplified)
                        # In a full implementation, we'd check for checkmate/stalemate

                        # If this is not the last token, continue to next move
                        # If this is the last token, we'll fall through to show final board
                    else:
                        # Algebraic notation parsing succeeded but move was rejected
                        print(f"\n- INVALID MOVE: {move_token}")
                        print(f"  Reason: {result['reason']}")
                        print_board(game_state)
                        # Stop processing further moves in this line
                        break

                except Exception as e:
                    # Fall back to coordinate parsing for backward compatibility
                    print(f"\n! Exception in algebraic parsing: {type(e).__name__}: {e}")
                    print(f"* Attempting to parse '{move_token}' (coordinate fallback)...")

                    # Try coordinate format first (e2e4)
                    if len(move_token) == 4 and move_token[0] in 'abcdefgh' and move_token[1] in '12345678' and \
                       move_token[2] in 'abcdefgh' and move_token[3] in '12345678':
                        from_square = move_token[0:2]
                        to_square = move_token[2:4]

                        result = validator.validate_move(from_square, to_square)

                        if result['accepted']:
                            print(f"\n+ VALID MOVE: {from_square}->{to_square}")
                            print(f"  Reason: {result['reason']}")

                            game_state.make_move(from_square, to_square)

                            if result.get('is_check'):
                                print(f"  {move_token}+ (Check!)")

                            print_board(game_state)
                            move_number += 1

                            # If this is not the last token, continue to next move
                        else:
                            print(f"\n- INVALID MOVE: {from_square}->{to_square}")
                            print(f"  Reason: {result['reason']}")
                            print_board(game_state)
                            # Stop processing further moves in this line
                            break
                    else:
                        print(f"  Invalid format. Please use:")
                        print(f"    - Algebraic notation: e4, Nf3, O-O, exd5, e8=Q")
                        print(f"    - Coordinate format: e2e4, g1f3 (e.g., e2e4 for pawn from e2 to e4)")
                        print_board(game_state)
                        # Stop processing further moves in this line
                        break

            # After processing all tokens (or stopping due to error), continue to next input prompt
            # The board has already been printed after the last successful move

        except KeyboardInterrupt:
            print("\n\nGame interrupted. Thanks for playing!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")
            print_board(game_state)


if __name__ == "__main__":
    main()