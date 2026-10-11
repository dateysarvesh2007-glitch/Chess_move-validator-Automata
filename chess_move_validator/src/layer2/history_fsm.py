"""
History-dependent Finite State Machine for tracking game state information.
This demonstrates Layer 2 of the four-layer architecture.

The history FSM tracks information that depends on previous moves:
- Whether kings and rooks have moved (for castling)
- The immediately previous move (for en passant)
- En passant target square

Unlike the DFAs in Layer 1 which only need current board state,
this FSM requires access to historical information to validate
history-dependent rules like castling and en passant.

The FSM maintains explicit state rather than using hidden globals.
"""

from game_state import GameState
from coordinates import square_to_coordinates


class HistoryFSM:
    """
    Finite State Machine that tracks historical game information
    needed for castling and en passant validation.
    """

    def __init__(self, game_state):
        """
        Initialize the history FSM with a reference to game state.

        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state
        # No additional state needed beyond what's in game_state
        # The FSM's "state" is the game_state itself

    def update(self, move_record):
        """
        Update the FSM state based on a move that was just made.
        This is called after a move is validated and executed.

        Args:
            move_record (dict): Information about the move that was made
        """
        # The game_state already handles updating its own history
        # through its make_move method, so this is primarily
        # a placeholder for FSM-style thinking
        pass

    def can_castle_kingside(self, color):
        """
        Check if kingside castling is currently possible for the given color.

        Args:
            color (str): 'white' or 'black'

        Returns:
            bool: True if kingside castling is allowed, False otherwise
        """
        return self.game_state.castling_rights[color]['kingside']

    def can_castle_queenside(self, color):
        """
        Check if queenside castling is currently possible for the given color.

        Args:
            color (str): 'white' or 'black'

        Returns:
            bool: True if queenside castling is allowed, False otherwise
        """
        return self.game_state.castling_rights[color]['queenside']

    def get_en_passant_target(self):
        """
        Get the current en passant target square, if any.

        Returns:
            str or None: The en passant target square (e.g., "e6") or None
        """
        return self.game_state.en_passant_target

    def get_last_move(self):
        """
        Get the immediately previous move, if any.

        Returns:
            dict or None: The last move record, or None if no moves made
        """
        history = self.game_state.move_history
        return history[-1] if history else None

    def is_en_passant_available(self, color, pawn_square, target_square):
        """
        Check if an en passant capture is legally possible.

        Args:
            color (str): 'white' or 'black' (color of the pawn attempting capture)
            pawn_square (str): Current square of the pawn (e.g., "e5")
            target_square (str): Target square for capture (e.g., "d6")

        Returns:
            bool: True if en passant capture is legal, False otherwise
        """
        # En passant is only possible if:
        # 1. There is an en passant target square
        # 2. The target square matches the en passant target
        # 3. The pawn is on its 5th rank (white: rank 5, black: rank 4)
        # 4. The capture is diagonal (adjacent file)

        en_passant_target = self.get_en_passant_target()
        if en_passant_target is None:
            return False

        if target_square != en_passant_target:
            return False

        # Check if pawn is on the correct rank for en passant
        pawn_row, pawn_col = square_to_coordinates(pawn_square)
        target_row, target_col = square_to_coordinates(target_square)

        # Pawn must be on 5th rank for white (row 4) or 4th rank for black (row 3)
        correct_rank = (color == 'white' and pawn_row == 4) or (color == 'black' and pawn_row == 3)
        if not correct_rank:
            return False

        # Must be diagonal capture (adjacent files)
        if abs(pawn_col - target_col) != 1:
            return False

        # The captured pawn should be on the same file as target, but opposite color's pawn rank
        # For white capturing: black pawn on rank 4 (row 3)
        # For black capturing: white pawn on rank 5 (row 4)
        expected_captured_row = target_row  # The en passant target is where the captured pawn *was*
        actual_captured_row = target_row - (1 if color == 'white' else -1)

        # Check if there's an enemy pawn on the expected square
        captured_square = f"{target_square[0]}{chr(ord('1') + actual_captured_row)}"
        target_piece = self.game_state.board.get_piece(captured_square)

        return (target_piece is not None and
                target_piece.piece_type == 'pawn' and
                target_piece.color != color)

    def has_king_moved(self, color):
        """
        Check if the king of the given color has moved from its starting position.

        Args:
            color (str): 'white' or 'black'

        Returns:
            bool: True if king has moved, False otherwise
        """
        # Check if king is still on starting square
        if color == 'white':
            king_piece = self.game_state.board.get_piece('e1')
            return king_piece is None or king_piece.piece_type != 'king' or king_piece.color != 'white'
        else:  # black
            king_piece = self.game_state.board.get_piece('e8')
            return king_piece is None or king_piece.piece_type != 'king' or king_piece.color != 'black'

    def has_rook_moved(self, color, side):
        """
        Check if a specific rook has moved from its starting position.

        Args:
            color (str): 'white' or 'black'
            side (str): 'kingside' or 'queenside'

        Returns:
            bool: True if rook has moved, False otherwise
        """
        if color == 'white':
            if side == 'kingside':
                rook_piece = self.game_state.board.get_piece('h1')
                return rook_piece is None or rook_piece.piece_type != 'rook' or rook_piece.color != 'white'
            else:  # queenside
                rook_piece = self.game_state.board.get_piece('a1')
                return rook_piece is None or rook_piece.piece_type != 'rook' or rook_piece.color != 'white'
        else:  # black
            if side == 'kingside':
                rook_piece = self.game_state.board.get_piece('h8')
                return rook_piece is None or rook_piece.piece_type != 'rook' or rook_piece.color != 'black'
            else:  # queenside
                rook_piece = self.game_state.board.get_piece('a8')
                return rook_piece is None or rook_piece.piece_type != 'rook' or rook_piece.color != 'black'


# Automata Theory Notes for History FSM:
# The History FSM demonstrates why some rules require more than a DFA:
#
# STATES: Conceptually, the FSM state is the entire game_state object
#         which includes:
#         - castling_rights: Track whether king/rooks have moved
#         - en_passant_target: Track opportunity from last move
#         - move_history: Complete sequence of moves
#
# TRANSITIONS: Occur when make_move() is called on game_state
#              Updates castling rights based on king/rook movement
#              Updates en passant target based on pawn double-advance
#
# WHY FSM INSTEAD OF DFA:
# 1. **Castling**: Requires knowing if king/rook ever moved (unbounded history)
# 2. **En passant**: Requires knowing what the *immediately previous* move was
# 3. These require memory of arbitrary-length history, which a DFA cannot provide
#
# A DFA has fixed, finite memory (its states). An FSM can have
# memory that grows with input length (like tracking move history).
#
# This clearly demonstrates the computational difference:
# - Layer 1 (piece movement): DFA-sufficient (only current board matters)
# - Layer 2 (castling, en passant): Requires FSM (need historical information)