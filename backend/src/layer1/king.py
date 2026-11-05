"""
King movement validator implemented as a Deterministic Finite Automaton (DFA).
This demonstrates Layer 1 of the four-layer architecture.

The king DFA validates whether a king can move from one square to another
according to chess rules, considering:
- Kings move one square in any direction (horizontal, vertical, or diagonal)
- Castling is handled by Layer 2 (history-dependent FSM)
- Cannot move onto squares occupied by pieces of the same color
- Can capture enemy pieces by moving onto their square

Note: This DFA only handles normal king movement (one square).
Castling validation is performed by Layer 2.

DFA STATES:
- START: Initial state, waiting to validate movement
- ONE_SQUARE_MOVE: Movement is exactly one square in any direction
- DESTINATION_REACHED: Successfully reached destination square
- INVALID_DISTANCE: Movement is more than one square in any direction
- INVALID_DESTINATION: Destination has friendly piece or is same square

ALPHABET (input conditions):
- Distance exactly one square? (max(abs(delta_row), abs(delta_col)) == 1)
- Destination square empty?
- Destination square has enemy piece?
- Destination square has friendly piece?
- Same square (no movement)?

TRANSITION LOGIC:
START
  |
  +--[distance_is_one]--> ONE_SQUARE_MOVE
  |
  +--[otherwise]--> INVALID_DISTANCE

ONE_SQUARE_MOVE
  |
  +--[empty_or_enemy]--> DESTINATION_REACHED
  |
  +--[friendly]--> INVALID_DESTINATION

ACCEPTING STATE: DESTINATION_REACHED
REJECTING STATES: INVALID_DISTANCE, INVALID_DESTINATION
"""

from coordinates import square_to_coordinates
from piece import Piece


class KingDFA:
    """
    Deterministic Finite Automaton for validating king movements (normal moves only).
    Castling is handled by Layer 2.
    """

    def __init__(self):
        """Initialize the king DFA."""
        self.reset()

    def reset(self):
        """Reset the DFA to the starting state."""
        self.state = 'START'
        self.start_pos = None
        self.end_pos = None
        self.board = None

    def validate(self, board, from_square, to_square):
        """
        Validate a king move using the DFA.

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
        if not start_piece or start_piece.piece_type != 'king':
            return {'valid': False, 'reason': "No king at starting position"}

        # START STATE: Check if movement is exactly one square
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos

        delta_row = abs(end_row - start_row)
        delta_col = abs(end_col - start_col)

        # King moves exactly one square in any direction
        # max(delta_row, delta_col) == 1 ensures we move at most one square in each direction
        if max(delta_row, delta_col) == 1:
            self.state = 'ONE_SQUARE_MOVE'
        else:
            self.state = 'INVALID_DISTANCE'
            return {'valid': False, 'reason': "Kings move exactly one square in any direction"}

        # Process ONE_SQUARE_MOVE state
        if self.state == 'ONE_SQUARE_MOVE':
            # Check destination square
            end_piece = self.board.get_piece(to_square)
            if end_piece is None:
                # Empty square - valid move
                self.state = 'DESTINATION_REACHED'
            elif end_piece.color != start_piece.color:
                # Enemy piece - valid capture
                self.state = 'DESTINATION_REACHED'
            else:
                # Friendly piece - invalid move
                self.state = 'INVALID_DESTINATION'

        # Return result based on final state
        if self.state == 'DESTINATION_REACHED':
            return {'valid': True, 'reason': "Legal king move"}
        else:
            return {'valid': False, 'reason': self._get_rejection_reason()}

    def _get_rejection_reason(self):
        """
        Get a human-readable reason for rejection based on the final state.

        Returns:
            str: Explanation of why the move was rejected
        """
        if self.state == 'INVALID_DISTANCE':
            return "Kings move exactly one square in any direction"
        elif self.state == 'INVALID_DESTINATION':
            return "Cannot move onto a square occupied by your own piece"
        else:
            return "Invalid king move"


# Automata Theory Notes for King DFA:
# The king DFA is one of the simplest piece DFAs:
#
# STATES: START, ONE_SQUARE_MOVE, DESTINATION_REACHED, INVALID_DISTANCE, INVALID_DESTINATION
#
# Why it's simple:
# 1. All valid moves are exactly one square away
# 2. No path checking needed (maximum distance is 1)
# 3. Movement is uniform in all 8 directions
#
# This demonstrates how the complexity of piece DFAs varies based on movement patterns:
# - Simple: king (one square in any direction)
# - Moderate: knight (fixed L-shape jumps)
# - More complex: sliding pieces (rook, bishop, queen - require path checking)
# - Most complex: pawn (direction-sensitive, special moves, captures-only diagonal)
#
# The king DFA shows that even simple movement rules benefit from explicit DFA modeling
# for educational clarity and consistency in the Layer 1 design.