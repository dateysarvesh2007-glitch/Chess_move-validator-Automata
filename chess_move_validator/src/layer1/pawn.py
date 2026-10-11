"""
Pawn movement validator implemented as a Deterministic Finite Automaton (DFA).
This demonstrates Layer 1 of the four-layer architecture.

The pawn DFA validates whether a pawn can move from one square to another
according to chess rules, considering:
- White pawns move up the board (increasing row index), black pawns move down
- Pawns move forward one square, or two squares from starting position
- Pawns capture diagonally one square forward
- En passant capture is handled by Layer 2 (history-dependent)
- Promotion is handled by Layer 3 (move validation)
- Cannot move backward
- Cannot move through or onto pieces of the same color
- Can capture enemy pieces by moving diagonally onto their square

DFA STATES:
- START: Initial state, waiting to determine move type
- FORWARD_ONE: Moving forward one square
- FORWARD_TWO: Moving forward two squares (from starting rank only)
- DIAGONAL_CAPTURE: Moving diagonally one square (capture only)
- PATH_CLEAR: Path is clear so far (for forward moves)
- BLOCKED: Path is blocked by a piece
- DESTINATION_REACHED: Successfully reached destination square
- INVALID_DIRECTION: Movement is not valid for a pawn
- INVALID_DESTINATION: Destination has friendly piece or movement violates rules

ALPHABET (input conditions):
- Moving forward? (direction depends on color)
- Starting rank? (rank 2 for white, rank 7 for black)
- Same file? (delta_file == 0)
- Adjacent file? (abs(delta_file) == 1)
- Forward one square? (delta_rank == 1 for white, -1 for black)
- Forward two squares? (delta_rank == 2 for white, -2 for black)
- Diagonal forward? (abs(delta_file)==1 and delta_rank==1 for white, -1 for black)
- Path clear to next square?
- Destination square empty?
- Destination square has enemy piece? (required for diagonal moves)
- Destination square has friendly piece?
- Same square (no movement)?

TRANSITION LOGIC (WHITE PAWN EXAMPLE - BLACK IS SYMMETRICAL):
START
  |
  +--[forward_one AND same_file]--> FORWARD_ONE
  |
  +--[forward_two AND starting_rank AND same_file]--> FORWARD_TWO
  |
  +--[diagonal_forward AND adjacent_file]--> DIAGONAL_CAPTURE
  |
  +--[otherwise]--> INVALID_DIRECTION

FORWARD_ONE
  |
  +--[path_clear AND last AND empty]--> DESTINATION_REACHED
  |
  +--[path_clear AND last AND friendly/enemy]--> INVALID_DESTINATION (can't capture forward)
  |
  +--[not_path_clear]--> BLOCKED

FORWARD_TWO
  |
  +--[first_square_empty AND second_square_empty]--> DESTINATION_REACHED
  |
  +--[first_square_not_empty]--> BLOCKED
  |
  +--[second_square_not_empty]--> BLOCKED

DIAGONAL_CAPTURE
  |
  +--[enemy_piece]--> DESTINATION_REACHED
  |
  +--[empty_or_friendly]--> INVALID_DESTINATION (must capture to move diagonally)

ACCEPTING STATE: DESTINATION_REACHED
REJECTING STATES: BLOCKED, INVALID_DIRECTION, INVALID_DESTINATION
"""

from coordinates import square_to_coordinates, coordinates_to_square


class PawnDFA:
    """
    Deterministic Finite Automaton for validating pawn movements.
    Note: En passant and promotion are handled by higher layers.
    """

    def __init__(self):
        """Initialize the pawn DFA."""
        self.reset()

    def reset(self):
        """Reset the DFA to the starting state."""
        self.state = 'START'
        self.start_pos = None
        self.end_pos = None
        self.board = None
        self.piece_color = None
        self.direction = None  # +1 for white (up), -1 for black (down)
        self.start_rank = None  # Rank 2 for white, 7 for black

    def validate(self, board, from_square, to_square):
        """
        Validate a pawn move using the DFA.

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
        if not start_piece or start_piece.piece_type != 'pawn':
            return {'valid': False, 'reason': "No pawn at starting position"}

        self.piece_color = start_piece.color

        # Set direction and starting rank based on color
        if self.piece_color == 'white':
            self.direction = 1  # White moves up (increasing row index)
            self.start_rank = 1  # Rank 2 -> index 1
        else:  # black
            self.direction = -1  # Black moves down (decreasing row index)
            self.start_rank = 6  # Rank 7 -> index 6

        # START STATE: Determine move type based on color-specific rules
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos

        delta_row = end_row - start_row
        delta_col = end_col - start_col

        # Check forward one square move
        if delta_row == self.direction and delta_col == 0:
            self.state = 'FORWARD_ONE'
        # Check forward two squares move (only from starting rank)
        elif delta_row == 2 * self.direction and delta_col == 0 and start_row == self.start_rank:
            self.state = 'FORWARD_TWO'
        # Check diagonal capture (one square forward diagonally)
        elif abs(delta_col) == 1 and delta_row == self.direction:
            self.state = 'DIAGONAL_CAPTURE'
        else:
            self.state = 'INVALID_DIRECTION'
            return {'valid': False, 'reason': self._get_invalid_direction_reason()}

        # Process transitions based on move type
        if self.state == 'FORWARD_ONE':
            self._process_forward_one()
        elif self.state == 'FORWARD_TWO':
            self._process_forward_two()
        elif self.state == 'DIAGONAL_CAPTURE':
            self._process_diagonal_capture()

        # Return result based on final state
        if self.state == 'DESTINATION_REACHED':
            return {'valid': True, 'reason': self._get_accept_reason()}
        else:
            return {'valid': False, 'reason': self._get_rejection_reason()}

    def _process_forward_one(self):
        """Process forward one square move."""
        end_piece = self.board.get_piece_at(self.end_pos[0], self.end_pos[1])
        if end_piece is None:
            # Empty square - valid move
            self.state = 'DESTINATION_REACHED'
        else:
            # Occupied square - can't move forward onto any piece
            self.state = 'INVALID_DESTINATION'

    def _process_forward_two(self):
        """Process forward two squares move."""
        start_row, start_col = self.start_pos
        # Check intermediate square
        mid_row = start_row + self.direction
        mid_piece = self.board.get_piece_at(mid_row, start_col)
        if mid_piece is not None:
            # Blocked by piece on first square
            self.state = 'BLOCKED'
            return

        # Check destination square
        end_piece = self.board.get_piece_at(self.end_pos[0], self.end_pos[1])
        if end_piece is None:
            # Empty square - valid move
            self.state = 'DESTINATION_REACHED'
        else:
            # Occupied square - can't move forward onto any piece
            self.state = 'INVALID_DESTINATION'

    def _process_diagonal_capture(self):
        """Process diagonal capture move."""
        end_piece = self.board.get_piece_at(self.end_pos[0], self.end_pos[1])
        if end_piece is not None and end_piece.color != self.piece_color:
            # Enemy piece - valid capture
            self.state = 'DESTINATION_REACHED'
        else:
            # Empty square or friendly piece - invalid (can't move diagonally without capturing)
            self.state = 'INVALID_DESTINATION'

    def _get_invalid_direction_reason(self):
        """Get reason for invalid direction based on pawn color and move distance."""
        start_row, start_col = self.start_pos
        end_row, end_col = self.end_pos
        delta_row = end_row - start_row

        if self.piece_color == 'white':
            # White pawns move toward increasing row numbers
            if delta_row > 2:
                if delta_row == 3:
                    return "White pawn cannot move three squares forward (maximum two squares)"
                else:
                    return f"White pawn cannot move {delta_row} squares forward (maximum two squares)"
            elif delta_row < 0:
                return "White pawns move forward (toward increasing row numbers), not backward"
            elif abs(end_col - start_col) > 1:
                return "White pawns move straight forward or capture diagonally one square to the side"
            else:
                return "White pawns move forward one square, or two from start rank, or capture diagonally forward"
        else:
            # Black pawns move toward decreasing row numbers
            if delta_row < -2:
                if delta_row == -3:
                    return "Black pawn cannot move three squares forward (maximum two squares)"
                else:
                    return f"Black pawn cannot move {abs(delta_row)} squares forward (maximum two squares)"
            elif delta_row > 0:
                return "Black pawns move forward (toward decreasing row numbers), not forward"
            elif abs(end_col - start_col) > 1:
                return "Black pawns move straight forward or capture diagonally one square to the side"
            else:
                return "Black pawns move forward one square, or two from start rank, or capture diagonally forward"

    def _get_rejection_reason(self):
        """
        Get a human-readable reason for rejection based on the final state.

        Returns:
            str: Explanation of why the move was rejected
        """
        if self.state == 'BLOCKED':
            return "Path is blocked by another piece"
        elif self.state == 'INVALID_DIRECTION':
            return self._get_invalid_direction_reason()
        elif self.state == 'INVALID_DESTINATION':
            # More specific reasons for invalid destination
            start_row, start_col = self.start_pos
            end_row, end_col = self.end_pos

            if abs(end_col - start_col) == 0 and abs(end_row - start_row) > 0:
                # Forward movement blocked or occupied
                if self.piece_color == 'white':
                    return "Pawn cannot move forward onto an occupied square"
                else:
                    return "Pawn cannot move forward onto an occupied square"
            elif abs(end_col - start_col) == 1 and abs(end_row - start_row) == 1:
                # Diagonal movement
                end_piece = self.board.get_piece_at(self.end_pos[0], self.end_pos[1])
                if end_piece is None:
                    return "Pawns can only move diagonally to capture an enemy piece"
                elif end_piece.color == self.piece_color:
                    return "Cannot move onto a square occupied by your own piece"
                else:
                    return "Invalid pawn diagonal move"
            else:
                return "Invalid pawn move"
        else:
            return "Invalid pawn move"

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

        if abs(delta_col) == 0 and abs(delta_row) == 1:
            if self.piece_color == 'white':
                return "Legal one-square pawn advance"
            else:
                return "Legal one-square pawn advance"
        elif abs(delta_col) == 0 and abs(delta_row) == 2:
            if self.piece_color == 'white':
                return "Legal two-square pawn advance from starting rank"
            else:
                return "Legal two-square pawn advance from starting rank"
        elif abs(delta_col) == 1 and abs(delta_row) == 1:
            captured_piece = self.board.get_piece_at(self.end_pos[0], self.end_pos[1])
            if captured_piece:
                if self.piece_color == 'white':
                    return "Legal pawn capture"
                else:
                    return "Legal pawn capture"
            else:
                # This shouldn't happen in DIAGONAL_CAPTURE state, but just in case
                return "Legal pawn diagonal move"
        else:
            return "Legal pawn move"


# Automata Theory Notes for Pawn DFA:
# The pawn DFA shows how movement rules can become more complex:
#
# STATES: START, FORWARD_ONE, FORWARD_TWO, DIAGONAL_CAPTURE,
#         BLOCKED, DESTINATION_REACHED, INVALID_DIRECTION, INVALID_DESTINATION
#
# Key complexities:
# 1. Direction-dependent movement (white vs black)
# 2. Special two-step move only from starting rank
# 3. Diagonal movement only allowed for captures
# 4. Asymmetric rules (forward vs diagonal movement)
#
# Despite these complexities, it still follows DFA principles:
# - Deterministic state transitions based on input conditions
# - Clear accepting and rejecting states
# - Input alphabet based on board conditions and move characteristics
#
# Note: En passant and promotion are intentionally omitted from this DFA
# because they depend on game history (en passant) or require special
# handling (promotion), demonstrating Layer 2 and Layer 3 responsibilities.