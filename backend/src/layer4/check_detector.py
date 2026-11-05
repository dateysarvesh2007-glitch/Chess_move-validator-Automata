"""
Check detector that identifies when a move gives check to the opponent.
This works with Layer 4 to automatically generate the '+' notation.
"""

from layer1.rook import RookDFA
from layer1.bishop import BishopDFA
from layer1.knight import KnightDFA
from layer1.pawn import PawnDFA
from layer1.king import KingDFA
from layer1.queen import QueenDFA
from game_state import GameState
from coordinates import square_to_coordinates, coordinates_to_square


class CheckDetector:
    """
    Detects when a move gives check to the opponent.
    """

    def __init__(self, game_state):
        """
        Initialize the check detector.

        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state

        # Initialize Layer 1 validators (we reuse these for attack detection)
        self.attack_validators = {
            'rook': RookDFA(),
            'bishop': BishopDFA(),
            'knight': KnightDFA(),
            'pawn': PawnDFA(),
            'king': KingDFA(),
            'queen': QueenDFA()
        }

    def is_check(self, game_state, from_square, to_square, color):
        """
        Check if a move gives check to the opponent.

        Args:
            game_state (GameState): The game state after the move was made
            from_square (str): Starting square of the move
            to_square (str): Destination square of the move
            color (str): 'white' or 'black' (color of the moving player)

        Returns:
            bool: True if the move gives check, False otherwise
        """
        # Find the opponent's king
        opponent_color = 'black' if color == 'white' else 'white'
        opponent_king_square = game_state.get_king_position(opponent_color)

        if opponent_king_square is None:
            return False  # Shouldn't happen in valid chess

        # Check if any of our pieces can attack the opponent king
        # This is the same logic as in SafetyFilter but for our own pieces
        return self._is_square_attacked_by_us(game_state, opponent_king_square, color)

    def _is_square_attacked_by_us(self, game_state, target_square, our_color):
        """
        Check if any of our pieces can attack the target square.

        Args:
            game_state (GameState): The game state to check
            target_square (str): The square to check for attacks (e.g., "e8")
            our_color (str): 'white' or 'black' (color of our pieces)

        Returns:
            bool: True if any of our pieces can attack the square, False otherwise
        """
        # Check all squares on the board for our pieces
        for row in range(8):
            for col in range(8):
                piece = game_state.board.get_piece_at(row, col)
                if piece is not None and piece.color == our_color:
                    # Check if this piece can attack the target square
                    from_square = coordinates_to_square(row, col)
                    if self._can_piece_attack_square(game_state, piece, from_square, target_square):
                        return True  # Found an attacker - we give check

        return False  # None of our pieces can attack the square

    def _can_piece_attack_square(self, game_state, piece, from_square, to_square):
        """
        Check if a specific piece can attack a target square.
        Reuses Layer 1 movement logic but accounts for piece-specific attack patterns.

        Args:
            game_state (GameState): The game state to check
            piece (Piece): The piece that might be attacking
            from_square (str): Starting square of the piece
            to_square (str): Target square to check

        Returns:
            bool: True if the piece can attack the square, False otherwise
        """
        # Special handling for pawns: attack squares are different from movement squares
        if piece.piece_type == 'pawn':
            return self._can_pawn_attack_square(game_state, piece, from_square, to_square)

        # For all other pieces, attack movement is the same as normal movement
        validator = self.attack_validators.get(piece.piece_type)
        if validator is None:
            return False

        # Use the piece's normal movement validator to check if it can move to target
        # This works for rook, bishop, knight, queen, king
        result = validator.validate(game_state.board, from_square, to_square)
        return result['valid']

    def _can_pawn_attack_square(self, game_state, piece, from_square, to_square):
        """
        Check if a pawn can attack a target square.
        Pawns attack diagonally forward, not straight ahead.

        Args:
            game_state (GameState): The game state to check
            piece (Piece): The pawn piece
            from_square (str): Starting square of the pawn
            to_square (str): Target square to check

        Returns:
            bool: True if the pawn can attack the square, False otherwise
        """
        try:
            start_row, start_col = square_to_coordinates(from_square)
            target_row, target_col = square_to_coordinates(to_square)
        except ValueError:
            return False

        # Pawns attack one square diagonally forward
        delta_row = target_row - start_row
        delta_col = target_col - start_col

        if piece.color == 'white':
            # White pawns attack diagonally forward: one row up, one column left/right
            return (delta_row == 1 and abs(delta_col) == 1)
        else:  # black
            # Black pawns attack diagonally forward: one row down, one column left/right
            return (delta_row == -1 and abs(delta_col) == 1)


# Automata Theory Notes for Check Detector:
# This component works closely with Layer 4 (Safety Filter) but serves a different purpose:
#
# LAYER 4 (Safety Filter):
#   - Question: "Does OUR king get attacked by opponent after our move?"
#   - Logic: OR over opponent pieces attacking OUR king
#   - Purpose: Prevent illegal self-check moves
#
# CHECK DETECTOR:
#   - Question: "Does OUR move give check to opponent's king?"
#   - Logic: OR over OUR pieces attacking opponent's king
#   - Purpose: Generate '+' notation for valid moves that deliver check
#
# Both layers reuse the SAME Layer 1 movement logic:
# - Safety Filter: Uses Layer 1 to check if opponent can attack us
# - Check Detector: Uses Layer 1 to check if we can attack opponent
#
# This demonstrates beautiful code reuse and separation of concerns:
# - Layer 1: Defines how pieces move (reused by everyone)
# - Layer 2: Adds history dependence
# - Layer 3: Manages move sequence and turn order
# - Layer 4: Applies safety logic using Layer 1
# - Check Detector: Applies check detection logic using Layer 1
#
# The mathematical relationship is symmetric:
#   Safety: ¬(∃ opponent_piece: can_attack(opponent_piece, our_king))
#   Check:  ∃ our_piece: can_attack(our_piece, opponent_king)
#
# Where can_attack() is computed using Layer 1 DFAs.