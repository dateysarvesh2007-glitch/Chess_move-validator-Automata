"""
Castling validator that uses history-dependent information.
This demonstrates Layer 2 of the four-layer architecture.

The castling validator checks whether castling is legally possible
by examining historical information tracked by the History FSM:
- Whether the king has moved
- Whether the relevant rook has moved
- Whether squares between king and rook are empty
- Whether the king is currently in check
- Whether the king passes through or ends on attacked squares

Note: King safety (check) validation is performed by Layer 4.
This layer focuses on the historical and positional requirements.
"""

from .history_fsm import HistoryFSM
from coordinates import square_to_coordinates, coordinates_to_square
from piece import Piece


class CastlingValidator:
    """
    Validates castling moves using historical game information.
    """

    def __init__(self, game_state):
        """
        Initialize the castling validator.

        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state
        self.history_fsm = HistoryFSM(game_state)

    def validate_castling(self, color, kingside):
        """
        Validate whether castling is currently possible.

        Args:
            color (str): 'white' or 'black'
            kingside (bool): True for kingside castling, False for queenside

        Returns:
            dict: Validation result with 'valid' boolean and 'reason' string
        """
        # Determine which side we're checking
        side = 'kingside' if kingside else 'queenside'

        # Check 1: Has the king moved?
        if self.history_fsm.has_king_moved(color):
            return {
                'valid': False,
                'reason': f"Castling is illegal because the {color} king has moved"
            }

        # Check 2: Has the relevant rook moved?
        if self.history_fsm.has_rook_moved(color, side):
            rook_side = "kingside" if kingside else "queenside"
            return {
                'valid': False,
                'reason': f"Castling is illegal because the {color} {rook_side} rook has moved"
            }

        # Check 3: Are the squares between king and rook empty?
        if not self._is_path_clear(color, kingside):
            return {
                'valid': False,
                'reason': f"Castling is illegal because there are pieces blocking the path"
            }

        # Note: The following checks are typically handled by Layer 4 (safety filter):
        # - Is the king currently in check? (Layer 4)
        # - Does the king pass through check? (Layer 4)
        # - Does the king end up in check? (Layer 4)
        #
        # For educational purposes, we'll note what Layer 2 checks vs what Layer 4 checks

        return {
            'valid': True,
            'reason': f"All historical requirements for {color} {'kingside' if kingside else 'queenside'} castling are satisfied"
        }

    def _is_path_clear(self, color, kingside):
        """
        Check if the castling path is clear based on piece types.
        For castling to be possible, the relevant squares must be empty
        or contain friendly pieces that are not pawns (which don't block castling).

        Args:
            color (str): 'white' or 'black'
            kingside (bool): True for kingside, False for queenside

        Returns:
            bool: True if path is clear, False otherwise
        """
        if color == 'white':
            king_row = 0  # Rank 1 -> row 0
            if kingside:
                # Kingside: check f1 (column 5) - must be empty or have non-pawn friendly piece
                cols_to_check = [5]
            else:
                # Queenside: check d1 (column 3) - must be empty or have non-pawn friendly piece
                cols_to_check = [3]
        else:  # black
            king_row = 7  # Rank 8 -> row 7
            if kingside:
                # Kingside: check f8 (column 5) - must be empty or have non-pawn friendly piece
                cols_to_check = [5]
            else:
                # Queenside: check d8 (column 3) - must be empty or have non-pawn friendly piece
                cols_to_check = [3]

        # Check if the relevant squares are empty or have friendly non-pawn pieces
        for col in cols_to_check:
            piece = self.game_state.board.get_piece_at(king_row, col)
            if piece is not None:
                # If there's a piece, it must be a friendly non-pawn to not block castling
                if piece.color != color or piece.piece_type == 'pawn':
                    return False  # Blocked by enemy piece or pawn
        return True  # Path is clear (empty or friendly non-pawn pieces)

    def get_castling_move(self, color, kingside):
        """
        Get the standard castling move notation if castling is valid.

        Args:
            color (str): 'white' or 'black'
            kingside (bool): True for kingside castling, False for queenside

        Returns:
            tuple: (king_from, king_to, rook_from, rook_to) or None if invalid
        """
        validation = self.validate_castling(color, kingside)
        if not validation['valid']:
            return None

        if color == 'white':
            king_from = 'e1'
            if kingside:
                king_to = 'g1'
                rook_from = 'h1'
                rook_to = 'f1'
            else:
                king_to = 'c1'
                rook_from = 'a1'
                rook_to = 'd1'
        else:  # black
            king_from = 'e8'
            if kingside:
                king_to = 'g8'
                rook_from = 'h8'
                rook_to = 'f8'
            else:
                king_to = 'c8'
                rook_from = 'a8'
                rook_to = 'd8'

        return (king_from, king_to, rook_from, rook_to)


# Automata Theory Notes for Castling Validator:
# This validator shows how Layer 2 builds upon Layer 1:
#
# INPUTS:
# - Current board state (from Layer 1 perspective)
# - Historical information: king movement, rook movement (from History FSM)
#
# PROCESS:
# 1. Check historical facts using History FSM (Layer 2 responsibility)
# 2. Check current board configuration (path clarity - overlaps with Layer 1 concepts)
# 3. Defer safety checks to Layer 4 (king not in check, doesn't pass through check)
#
# This demonstrates the separation of concerns:
# - Layer 1: Basic movement patterns (DFA-sufficient)
# - Layer 2: History-dependent rules (requires FSM)
# - Layer 3: Move sequencing and turn management
# - Layer 4: Safety validation (check detection)
#
# The castling validator focuses on what makes Layer 2 necessary:
# Dependence on unbounded historical information (has king ever moved?)