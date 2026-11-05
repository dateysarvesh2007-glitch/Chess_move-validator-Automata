"""
Knight movement validator implemented as a Deterministic Finite Automaton (DFA).
This demonstrates Layer 1 of the four-layer architecture.

The knight DFA validates whether a knight can move from one square to another
according to chess rules, considering:
- Knights move in an L-shape: 2 squares in one direction and 1 square perpendicular
- Knights can jump over other pieces (no path checking)
- Cannot move onto squares occupied by pieces of the same color
- Can capture enemy pieces by moving onto their square

DFA STATES:
- START: Initial state, waiting to validate movement
- VALID_L_SHAPE: Movement forms a valid L-shape (2+1 or 1+2)
- DESTINATION_REACHED: Successfully reached destination square
- INVALID_L_SHAPE: Movement does not form a valid L-shape
- INVALID_DESTINATION: Destination has friendly piece or is same square

ALPHABET (input conditions):
- Forms L-shape? (abs(delta_row)==2 and abs(delta_col)==1) OR (abs(delta_row)==1 and abs(delta_col)==2)
- Destination square empty?
- Destination square has enemy piece?
- Destination square has friendly piece?
- Same square (no movement)?

TRANSITION LOGIC:
START
  |
  +--[valid_L_shape]--> VALID_L_SHAPE
  |
  +--[otherwise]--> INVALID_L_SHAPE

VALID_L_SHAPE
  |
  +--[empty_or_enemy]--> DESTINATION_REACHED
  |
  +--[friendly]--> INVALID_DESTINATION

ACCEPTING STATE: DESTINATION_REACHED
REJECTING STATES: INVALID_L_SHAPE, INVALID_DESTINATION
"""

from coordinates import square_to_coordinates
from piece import Piece


class KnightDFA:
    """
    Deterministic Finite Automaton for validating knight movements.
    """

    def __init__(self):
        """Initialize the knight DFA."""
        self.reset()

    def reset(self):
        """Reset the DFA to the starting state."""
        self.state = 'START'
        self.start_pos = None
        self.end_pos = None
        self.board = None

    def validate(self, board, from_square, to_square):
        """
        Validate a knight move using the DFA.

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
        if not start_piece or start_piece.piece_type != 'knight':
            return {'valid': False, 'reason': "No knight at starting position"}

        # START STATE: Check if movement forms a valid L-shape
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos

        delta_row = abs(end_row - start_row)
        delta_col = abs(end_col - start_col)

        # Knight moves: (2,1) or (1,2) in any direction
        if (delta_row == 2 and delta_col == 1) or (delta_row == 1 and delta_col == 2):
            self.state = 'VALID_L_SHAPE'
        else:
            self.state = 'INVALID_L_SHAPE'
            return {'valid': False, 'reason': "Knights move in L-shape: 2 squares in one direction, 1 in perpendicular"}

        # Process VALID_L_SHAPE state
        if self.state == 'VALID_L_SHAPE':
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
            return {'valid': True, 'reason': "Legal knight move"}
        else:
            return {'valid': False, 'reason': self._get_rejection_reason()}

    def _get_rejection_reason(self):
        """
        Get a human-readable reason for rejection based on the final state.

        Returns:
            str: Explanation of why the move was rejected
        """
        if self.state == 'INVALID_L_SHAPE':
            return "Knights move in L-shape: 2 squares in one direction, 1 in perpendicular"
        elif self.state == 'INVALID_DESTINATION':
            return "Cannot move onto a square occupied by your own piece"
        else:
            return "Invalid knight move"


# Automata Theory Notes for Knight DFA:
# The knight DFA is simpler than sliding piece DFAs because knights jump:
#
# STATES: START, VALID_L_SHAPE, DESTINATION_REACHED, INVALID_L_SHAPE, INVALID_DESTINATION
#
# Key differences from sliding pieces:
# 1. No path checking needed (knights jump over pieces)
# 2. Movement validation is done in one step (no incremental processing)
# 3. The L-shape constraint creates a finite set of valid transitions
#
# This demonstrates how DFAs can vary in complexity based on the movement pattern:
# - Sliding pieces (rook, bishop, queen): Require path checking -> more states
# - Jumping pieces (knight, king): Single-step validation -> fewer states
#
# Yet all follow the same DFA principles: states, transitions based on input conditions,
# deterministic processing, and accepting/rejecting states.