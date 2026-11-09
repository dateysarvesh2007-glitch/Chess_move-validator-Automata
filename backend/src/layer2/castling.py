
"""
Castling validator.

Layer 2 checks castling rights, the king and rook positions,
and whether the squares between them are empty.

Layer 4 king-safety checks are performed by GameValidator.
"""

class CastlingValidator:
    def __init__(self, game_state):
        self.game_state = game_state

    def validate_castling(self, color, kingside):
        side = 'kingside' if kingside else 'queenside'

        if color not in ('white', 'black'):
            return {
                'valid': False,
                'reason': 'Invalid player color'
            }

        rights = self.game_state.castling_rights.get(color, {})

        # The recorded castling right is authoritative.
        if not rights.get(side, False):
            return {
                'valid': False,
                'reason': f"{color.capitalize()} no longer has {side} castling rights"
            }

        king_square = 'e1' if color == 'white' else 'e8'

        if kingside:
            rook_square = 'h1' if color == 'white' else 'h8'
            path_squares = (
                ['f1', 'g1'] if color == 'white'
                else ['f8', 'g8']
            )
        else:
            rook_square = 'a1' if color == 'white' else 'a8'
            path_squares = (
                ['b1', 'c1', 'd1'] if color == 'white'
                else ['b8', 'c8', 'd8']
            )

        king = self.game_state.board.get_piece(king_square)
        rook = self.game_state.board.get_piece(rook_square)

        if (
            king is None
            or king.piece_type != 'king'
            or king.color != color
        ):
            return {
                'valid': False,
                'reason': f"No {color} king on {king_square}"
            }

        if (
            rook is None
            or rook.piece_type != 'rook'
            or rook.color != color
        ):
            return {
                'valid': False,
                'reason': f"No {color} rook on {rook_square}"
            }

        # Every square between the king and rook must be empty.
        for square in path_squares:
            if self.game_state.board.get_piece(square) is not None:
                return {
                    'valid': False,
                    'reason': f"Castling path is blocked at {square}"
                }

        return {
            'valid': True,
            'kingside': kingside,
            'reason': (
                f"Historical and positional requirements for "
                f"{color} {side} castling are satisfied"
            )
        }

    def get_castling_move(self, color, kingside):
        validation = self.validate_castling(color, kingside)

        if not validation['valid']:
            return None

        if color == 'white':
            if kingside:
                return ('e1', 'g1', 'h1', 'f1')
            return ('e1', 'c1', 'a1', 'd1')

        if color == 'black':
            if kingside:
                return ('e8', 'g8', 'h8', 'f8')
            return ('e8', 'c8', 'a8', 'd8')

        return None


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