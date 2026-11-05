"""
En passant validator that uses history-dependent information.
This demonstrates Layer 2 of the four-layer architecture.

The en passant validator checks whether an en passant capture is legally possible
by examining historical information tracked by the History FSM:
- Whether the immediately previous move was a two-square pawn advance
- Whether the target pawn is adjacent to the capturing pawn
- Whether the capture happens immediately (only on the next move)

Note: Basic diagonal movement validation is handled by Layer 1 (pawn DFA).
This layer focuses on the historical requirements specific to en passant.
"""

from .history_fsm import HistoryFSM
from coordinates import square_to_coordinates


class EnPassantValidator:
    """
    Validates en passant captures using historical game information.
    """

    def __init__(self, game_state):
        """
        Initialize the en passant validator.

        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state
        self.history_fsm = HistoryFSM(game_state)

    def validate_en_passant(self, color, from_square, to_square):
        """
        Validate whether an en passant capture is legally possible.

        Args:
            color (str): 'white' or 'black' (color of the capturing pawn)
            from_square (str): Current square of the capturing pawn (e.g., "e5")
            to_square (str): Target square for capture (e.g., "d6")

        Returns:
            dict: Validation result with 'valid' boolean and 'reason' string
        """
        # Use the History FSM to check en passant availability
        is_available = self.history_fsm.is_en_passant_available(color, from_square, to_square)

        if is_available:
            return {
                'valid': True,
                'reason': "Legal en passant capture"
            }
        else:
            # Provide specific reasons for failure
            return self._get_rejection_reason(color, from_square, to_square)

    def _get_rejection_reason(self, color, from_square, to_square):
        """
        Get a human-readable reason for why en passant is not valid.

        Args:
            color (str): 'white' or 'black'
            from_square (str): Current square of the capturing pawn
            to_square (str): Target square for capture

        Returns:
            dict: Validation result with 'valid': False and reason string
        """
        # Check if there's an en passant target at all
        en_passant_target = self.history_fsm.get_en_passant_target()
        if en_passant_target is None:
            return {
                'valid': False,
                'reason': "No en passant opportunity available"
            }

        # Check if target matches en passant target
        if to_square != en_passant_target:
            return {
                'valid': False,
                'reason': f"En passant capture must be to square {en_passant_target}"
            }

        # Check if pawn is on correct rank
        try:
            pawn_row, pawn_col = square_to_coordinates(from_square)
            target_row, target_col = square_to_coordinates(to_square)
        except ValueError:
            return {
                'valid': False,
                'reason': "Invalid square notation"
            }

        # Pawn must be on 5th rank for white (row 4) or 4th rank for black (row 3)
        correct_rank = (color == 'white' and pawn_row == 4) or (color == 'black' and pawn_row == 3)
        if not correct_rank:
            expected_rank = "5th rank (row 4)" if color == 'white' else "4th rank (row 3)"
            return {
                'valid': False,
                'reason': f"Pawn must be on the {expected_rank} to perform en passant"
            }

        # Check if capture is diagonal (adjacent files)
        if abs(pawn_col - target_col) != 1:
            return {
                'valid': False,
                'reason': "En passant capture must be diagonal to an adjacent file"
            }

        # Check if there's actually an enemy pawn to capture
        # The captured pawn should be on the same file as target, but one rank toward the pawn
        captured_row = target_row - (1 if color == 'white' else -1)
        captured_square = f"{to_square[0]}{chr(ord('1') + captured_row)}"
        captured_piece = self.game_state.board.get_piece(captured_square)

        if captured_piece is None:
            return {
                'valid': False,
                'reason': "No enemy pawn to capture via en passant"
            }
        elif captured_piece.piece_type != 'pawn':
            return {
                'valid': False,
                'reason': "The piece to capture is not a pawn"
            }
        elif captured_piece.color == color:
            return {
                'valid': False,
                'reason': "Cannot capture your own piece via en passant"
            }

        # If we got here, something else is wrong (shouldn't happen with proper logic)
        return {
            'valid': False,
            'reason': "En passant capture conditions not met"
        }


# Automata Theory Notes for En Passant Validator:
# This validator clearly demonstrates Layer 2's responsibility:
#
# INPUTS:
# - Current board state (position of pawns)
# - Historical information: Was the previous move a two-square pawn advance?
#   (Available via History FSM's en_passant_target)
#
# PROCESS:
# 1. Check if en passant opportunity exists (History FSM responsibility)
# 2. Validate that the capture matches the opportunity (positional check)
# 3. Verify timing (en passant only available immediately after double-pawn advance)
#
# WHY THIS REQUIRES LAYER 2 (FSM):
# - En passant depends on the *immediately previous* move
# - This requires memory of at least the last move
# - A DFA cannot count or remember specific sequences of unbounded length
# - An FSM can track this limited history through its state
#
# The History FSM's en_passant_target field essentially stores:
# "Was the previous move a two-square pawn advance, and if so, where can it be captured?"
#
# This is a perfect example of a history-dependent rule that:
# 1. Cannot be implemented with a pure DFA (needs memory)
# 2. Can be implemented with an FSM (finite but unbounded history)
# 3. Is cleanly separated from basic movement validation (Layer 1)