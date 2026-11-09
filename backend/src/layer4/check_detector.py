"""
Check detector for identifying checks and king attacks.

Used by Layer 4 for king-safety checks and check detection.
"""

from layer1.rook import RookDFA
from layer1.bishop import BishopDFA
from layer1.knight import KnightDFA
from layer1.pawn import PawnDFA
from layer1.king import KingDFA
from layer1.queen import QueenDFA
from coordinates import square_to_coordinates, coordinates_to_square


class CheckDetector:
    """Detects attacks against kings and moves that give check."""

    def __init__(self, game_state):
        self.game_state = game_state

        self.attack_validators = {
            'rook': RookDFA(),
            'bishop': BishopDFA(),
            'knight': KnightDFA(),
            'pawn': PawnDFA(),
            'king': KingDFA(),
            'queen': QueenDFA()
        }

    def is_king_in_check(self, game_state, color):
        """
        Return True if the specified color's king is under attack.

        A missing king is treated as unsafe.
        """
        king_square = game_state.get_king_position(color)

        if king_square is None:
            return True

        opponent_color = 'black' if color == 'white' else 'white'

        return self._is_square_attacked_by_us(
            game_state,
            king_square,
            opponent_color
        )

    def is_check(self, game_state, from_square, to_square, color):
        """Check whether the moving player gives check to the opponent."""
        opponent_color = 'black' if color == 'white' else 'white'
        opponent_king_square = game_state.get_king_position(opponent_color)

        if opponent_king_square is None:
            return False

        return self._is_square_attacked_by_us(
            game_state,
            opponent_king_square,
            color
        )

    def _is_square_attacked_by_us(self, game_state, target_square, our_color):
        """Determine whether any piece of our color attacks a square."""
        for row in range(8):
            for col in range(8):
                piece = game_state.board.get_piece_at(row, col)

                if piece is not None and piece.color == our_color:
                    from_square = coordinates_to_square(row, col)

                    if self._can_piece_attack_square(
                        game_state, piece, from_square, target_square
                    ):
                        return True

        return False

    def _can_piece_attack_square(
        self, game_state, piece, from_square, to_square
    ):
        """Check whether a particular piece attacks a target square."""

        if piece.piece_type == 'pawn':
            return self._can_pawn_attack_square(
                game_state, piece, from_square, to_square
            )

        validator = self.attack_validators.get(piece.piece_type)

        if validator is None:
            return False

        result = validator.validate(
            game_state.board,
            from_square,
            to_square
        )

        return result['valid']

    def _can_pawn_attack_square(
        self, game_state, piece, from_square, to_square
    ):
        """Check diagonal pawn attacks, independent of target occupancy."""
        try:
            start_row, start_col = square_to_coordinates(from_square)
            target_row, target_col = square_to_coordinates(to_square)
        except ValueError:
            return False

        delta_row = target_row - start_row
        delta_col = target_col - start_col

        if piece.color == 'white':
            return delta_row == 1 and abs(delta_col) == 1

        return delta_row == -1 and abs(delta_col) == 1
