"""
Bishop movement validator implemented as a Deterministic Finite Automaton (DFA).
This demonstrates Layer 1 of the four-layer architecture.

The bishop DFA validates whether a bishop can move from one square to another
according to chess rules, considering:
- Bishops move diagonally any number of squares
- The path must be clear (no blocking pieces)
- Cannot move through or onto pieces of the same color
- Can capture enemy pieces by moving onto their square

DFA STATES:
- START: Initial state, waiting to determine movement direction
- SAME_DIAGONAL: Moving diagonally
- PATH_CLEAR: Path is clear so far, continuing to check
- BLOCKED: Path is blocked by a piece
- DESTINATION_REACHED: Successfully reached destination square
- INVALID_DIRECTION: Movement is not diagonal
- INVALID_DESTINATION: Destination has friendly piece or is same square

ALPHABET (input conditions):
- Same diagonal? (abs(delta_row) == abs(delta_col))
- Path clear to next square?
- Destination square empty?
- Destination square has enemy piece?
- Destination square has friendly piece?
- Same square (no movement)?

TRANSITION LOGIC:
START
  |
  +--[same_diagonal]--> SAME_DIAGONAL
  |
  +--[otherwise]--> INVALID_DIRECTION

SAME_DIAGONAL
  |
  +--[path_clear AND not_last]--> SAME_DIAGONAL (continue checking)
  |
  +--[path_clear AND last AND empty]--> DESTINATION_REACHED
  |
  +--[path_clear AND last AND enemy]--> DESTINATION_REACHED (capture)
  |
  +--[path_clear AND last AND friendly]--> INVALID_DESTINATION
  |
  +--[not_path_clear]--> BLOCKED

ACCEPTING STATE: DESTINATION_REACHED
REJECTING STATES: BLOCKED, INVALID_DIRECTION, INVALID_DESTINATION
"""

from coordinates import square_to_coordinates


class BishopDFA:
    """
    Deterministic Finite Automaton for validating bishop movements.
    """

    def __init__(self):
        """Initialize the bishop DFA."""
        self.reset()

    def reset(self):
        """Reset the DFA to the starting state."""
        self.state = 'START'
        self.start_pos = None
        self.end_pos = None
        self.board = None
        self.direction = None  # Will store step values
        self.step_row = 0      # -1, 0, or 1
        self.step_col = 0      # -1, 0, or 1
        self.current_row = 0
        self.current_col = 0

    def validate(self, board, from_square, to_square):
        """
        Validate a bishop move using the DFA.

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
        if not start_piece or start_piece.piece_type != 'bishop':
            return {'valid': False, 'reason': "No bishop at starting position"}

        # START STATE: Determine if movement is diagonal
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos

        delta_row = end_row - start_row
        delta_col = end_col - start_col

        # Check if moving diagonally (absolute values must be equal)
        if abs(delta_row) == abs(delta_col) and delta_row != 0:
            # Diagonal movement
            self.state = 'SAME_DIAGONAL'
            self.step_row = 1 if delta_row > 0 else -1
            self.step_col = 1 if delta_col > 0 else -1
        else:
            # Invalid direction - not diagonal
            self.state = 'INVALID_DIRECTION'
            return {'valid': False, 'reason': "Bishops move diagonally only"}

        # Initialize position checking
        self.current_row = start_row + self.step_row
        self.current_col = start_col + self.step_col

        # Process transitions until we reach an accepting or rejecting state
        while self.state not in ['DESTINATION_REACHED', 'BLOCKED', 'INVALID_DESTINATION']:
            self._process_transition()

        # Return result based on final state
        if self.state == 'DESTINATION_REACHED':
            # Check if destination has friendly piece
            end_piece = self.board.get_piece(to_square)
            if end_piece and end_piece.color == start_piece.color:
                return {'valid': False, 'reason': "Cannot move onto a square occupied by your own piece"}
            else:
                return {'valid': True, 'reason': "Legal bishop move"}
        else:
            return {'valid': False, 'reason': self._get_rejection_reason()}

    def _process_transition(self):
        """
        Process one transition in the DFA based on current state and board conditions.
        """
        if self.state == 'SAME_DIAGONAL':
            # Check if we've reached the destination
            if (self.current_row, self.current_col) == self.end_pos:
                # We're at the destination square
                end_piece = self.board.get_piece_at(self.current_row, self.current_col)
                if end_piece is None:
                    # Empty square - valid move
                    self.state = 'DESTINATION_REACHED'
                elif end_piece.color != self.board.get_piece(
                        self._square_from_pos(self.start_pos)).color:
                    # Enemy piece - valid capture
                    self.state = 'DESTINATION_REACHED'
                else:
                    # Friendly piece - invalid move
                    self.state = 'INVALID_DESTINATION'
            else:
                # We're still on the path - check if it's clear
                current_piece = self.board.get_piece_at(self.current_row, self.current_col)
                if current_piece is not None:
                    # Path is blocked
                    self.state = 'BLOCKED'
                else:
                    # Path is clear, continue to next square
                    self.current_row += self.step_row
                    self.current_col += self.step_col

        # Handle other states (shouldn't normally reach here in processing loop)
        elif self.state in ['INVALID_DIRECTION', 'BLOCKED', 'INVALID_DESTINATION']:
            # These are terminal states - no further processing needed
            pass

    def _get_rejection_reason(self):
        """
        Get a human-readable reason for rejection based on the final state.

        Returns:
            str: Explanation of why the move was rejected
        """
        if self.state == 'BLOCKED':
            return "Path is blocked by another piece"
        elif self.state == 'INVALID_DIRECTION':
            return "Bishops move diagonally only"
        elif self.state == 'INVALID_DESTINATION':
            return "Cannot move onto a square occupied by your own piece"
        else:
            return "Invalid bishop move"

    def _square_from_pos(self, pos):
        """
        Convert position tuple back to square string for piece lookup.

        Args:
            pos (tuple): (row, col) position

        Returns:
            str: Square in algebraic notation
        """
        from coordinates import coordinates_to_square
        return coordinates_to_square(pos[0], pos[1])


# Automata Theory Notes for Bishop DFA:
# Similar to the rook DFA, the bishop's movement follows a clear DFA pattern:
#
# STATES: START, SAME_DIAGONAL, BLOCKED, DESTINATION_REACHED, INVALID_DIRECTION, INVALID_DESTINATION
#
# The key insight is that both rook and bishop DFAs share similar structures
# but differ in their movement constraints:
# - Rook: delta_row == 0 XOR delta_col == 0 (but not both)
# - Bishop: abs(delta_row) == abs(delta_col) AND delta_row != 0
#
# This demonstrates how different piece movement rules can be captured
# by modifying the transition conditions in a similar DFA framework.