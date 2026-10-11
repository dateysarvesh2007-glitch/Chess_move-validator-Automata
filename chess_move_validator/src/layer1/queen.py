"""
Queen movement validator implemented as a Deterministic Finite Automaton (DFA).
This demonstrates Layer 1 of the four-layer architecture.

The queen DFA validates whether a queen can move from one square to another
according to chess rules, considering:
- Queens move like rooks OR bishops (horizontally, vertically, or diagonally)
- Can move any number of squares in those directions
- The path must be clear (no blocking pieces)
- Cannot move through or onto pieces of the same color
- Can capture enemy pieces by moving onto their square

DFA STATES:
- START: Initial state
- DESTINATION_REACHED: Successfully reached destination square
- BLOCKED: Path is blocked by a piece
- INVALID_DESTINATION: Destination has friendly piece
- INVALID_DIRECTION: Movement is not valid for a queen

ALPHABET (input conditions):
- Same file? (delta_col == 0)
- Same rank? (delta_row == 0)
- Diagonal? (abs(delta_row) == abs(delta_col))
- Path clear to next square?
- Destination square empty?
- Destination square has enemy piece?
- Destination square has friendly piece?

TRANSITION LOGIC:
START
  |
  +--[horizontal_or_vertical_or_diagonal AND path_clear]--> DESTINATION_REACHED
  |
  +--[horizontal_or_vertical_or_diagonal AND NOT path_clear]--> BLOCKED
  |
  +--[NOT (horizontal_or_vertical_or_diagonal)]--> INVALID_DIRECTION
  |
  +--[horizontal_or_vertical_or_diagonal AND path_clear AND friendly_destination]--> INVALID_DESTINATION

ACCEPTING STATE: DESTINATION_REACHED
REJECTING STATES: BLOCKED, INVALID_DESTINATION, INVALID_DIRECTION
"""

from coordinates import square_to_coordinates
from piece import Piece


class QueenDFA:
    """
    Deterministic Finite Automaton for validating queen movements.
    Validates horizontal, vertical, and diagonal movement with path checking.
    """

    def __init__(self):
        """Initialize the queen DFA."""
        self.reset()

    def reset(self):
        """Reset the DFA to the starting state."""
        self.state = 'START'
        self.board = None
        self.start_pos = None
        self.end_pos = None
        self.piece_color = None

    def validate(self, board, from_square, to_square):
        """
        Validate a queen move using the DFA.

        Args:
            board (Board): The current chess board
            from_square (str): Starting square (e.g., "e2")
            to_square (str): Destination square (e.g., "e4")

        Returns:
            dict: Validation result with 'valid' boolean and 'reason' string
        """
        # Reset for new validation
        self.reset()
        self.board = board

        # Validate input squares
        try:
            self.start_pos = square_to_coordinates(from_square)
            self.end_pos = square_to_coordinates(to_square)
        except ValueError as e:
            return {'valid': False, 'reason': f"Invalid square: {e}"}

        # Check if same square
        if self.start_pos == self.end_pos:
            return {'valid': False, 'reason': "Cannot move to the same square"}

        # Get the piece at start position
        start_piece = board.get_piece(from_square)
        if not start_piece or start_piece.piece_type != 'queen':
            return {'valid': False, 'reason': "No queen at starting position"}

        self.piece_color = start_piece.color

        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos

        delta_row = end_row - start_row
        delta_col = end_col - start_col

        # Check if the move is horizontal, vertical, or diagonal
        is_horizontal = (delta_row == 0 and delta_col != 0)
        is_vertical = (delta_col == 0 and delta_row != 0)
        is_diagonal = (abs(delta_row) == abs(delta_col) and delta_row != 0)

        if not (is_horizontal or is_vertical or is_diagonal):
            self.state = 'INVALID_DIRECTION'
            return {'valid': False, 'reason': "Queens move horizontally, vertically, or diagonally only"}

        # Check path is clear
        if not self._is_path_clear(start_row, start_col, end_row, end_col):
            self.state = 'BLOCKED'
            return {'valid': False, 'reason': "Path is blocked by another piece"}

        # Check destination square
        end_piece = board.get_piece_at(end_row, end_col)
        if end_piece is not None and end_piece.color == self.piece_color:
            self.state = 'INVALID_DESTINATION'
            return {'valid': False, 'reason': "Cannot move onto a square occupied by your own piece"}

        # If we get here, the move is valid
        self.state = 'DESTINATION_REACHED'
        return {'valid': True, 'reason': self._get_accept_reason()}

    def _is_path_clear(self, start_row, start_col, end_row, end_col):
        """
        Check if all squares between start and end are empty.

        Args:
            start_row, start_col: Starting position
            end_row, end_col: Ending position

        Returns:
            bool: True if path is clear, False otherwise
        """
        # Determine step direction
        row_step = 0 if end_row == start_row else (1 if end_row > start_row else -1)
        col_step = 0 if end_col == start_col else (1 if end_col > start_col else -1)

        # Start from the next square
        current_row, current_col = start_row + row_step, start_col + col_step

        # While we haven't reached the end square
        while (current_row, current_col) != (end_row, end_col):
            piece = self.board.get_piece_at(current_row, current_col)
            if piece is not None:
                return False  # Path is blocked
            current_row += row_step
            current_col += col_step

        return True  # All squares are empty

    def _get_accept_reason(self):
        """
        Get a human-readable reason for acceptance based on the move type.

        Returns:
            str: Explanation of why the move was accepted
        """
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos

        delta_row = end_row - start_row
        delta_col = end_col - start_col

        if abs(delta_col) == 0 and abs(delta_row) > 0:
            if self.piece_color == 'white':
                return "Linear vertical advance"
            else:
                return "Linear vertical advance"
        elif abs(delta_row) == 0 and abs(delta_col) > 0:
            if self.piece_color == 'white':
                return "Linear horizontal advance"
            else:
                return "Linear horizontal advance"
        else:
            # Diagonal move
            if self.piece_color == 'white':
                return "Diagonal advance"
            else:
                return "Diagonal advance"


# Automata Theory Notes for Queen DFA:
# The queen DFA demonstrates how movement rules can be combined:
#
# STATES: START, DESTINATION_REACHED, BLOCKED, INVALID_DESTINATION, INVALID_DIRECTION
#
# Key aspects:
# 1. The queen combines rook-like (horizontal/vertical) and bishop-like (diagonal) movement
# 2. Path checking is required for all queen moves (unlike king or knight)
# 3. The DFA checks direction first, then path, then destination
#
# Despite these complexities, it still follows DFA principles:
# - Deterministic state transitions based on input conditions
# - Clear accepting and rejecting states
# - Input alphabet based on board conditions and move characteristics
#
# This implementation shows how a complex movement pattern can be validated
# with a relatively simple DFA by breaking down the movement into
# horizontal, vertical, and diagonal components.