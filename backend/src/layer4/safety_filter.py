"""
Safety filter that checks if a move leaves the moving player's king in check.
This demonstrates Layer 4 of the four-layer architecture.

The safety filter implements the king safety check:
1. After Layers 1/2/3 say a move is otherwise valid:
2. Create a copy of the board/game state
3. Apply the proposed move to the copy
4. Find the moving side's king
5. Determine whether the opponent can attack that king
6. Reuse Layer 1 movement logic for the opponent's pieces
7. Combine possible attacks using OR logic
8. If any opposing piece can legally attack the king's square, reject the move
9. Otherwise accept it

This layer reuses Layer 1 instead of duplicating every piece's attack logic.
"""

from layer1.rook import RookDFA
from layer1.bishop import BishopDFA
from layer1.knight import KnightDFA
from layer1.pawn import PawnDFA
from layer1.king import KingDFA
from layer1.queen import QueenDFA
from game_state import GameState
from coordinates import square_to_coordinates, coordinates_to_square


class SafetyFilter:
    """
    Validates that a move does not leave the moving player's king in check.
    """

    def __init__(self, game_state):
        """
        Initialize the safety filter.

        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state

        # Initialize Layer 1 validators (we reuse these for attack detection)
        self.attack_validators = {
            'rook': RookDFA(),
            'bishop': BishopDFA(),
            'knight': KnightDFA(),
            'pawn': PawnDFA(),  # Note: pawn attack movement is different from normal movement
            'king': KingDFA(),
            'queen': QueenDFA()
        }

    def is_move_safe(self, game_state, from_square, to_square, color):
        """
        Check if a move is safe (doesn't leave own king in check).

        Args:
            game_state (GameState): The game state to check (usually a copy)
            from_square (str): Starting square of the move
            to_square (str): Destination square of the move
            color (str): 'white' or 'black' (color of the moving player)

        Returns:
            dict: {'safe': bool, 'reason': str}
        """
        # STEP 1: Make a copy of the board/game state (already done by caller)
        # STEP 2: Apply the proposed move to the copy (already done by caller)
        # STEP 3: Find the moving side's king
        king_square = game_state.get_king_position(color)
        if king_square is None:
            return {'safe': False, 'reason': f"No {color} king found on the board"}

        # STEP 4: Determine whether the opponent can attack that king
        opponent_color = 'black' if color == 'white' else 'white'

        # STEP 5-7: Check if any opponent piece can attack the king's square
        # Using OR logic: if ANY piece can attack, king is in check
        opponent_can_attack = self._is_square_attacked_by_opponent(
            game_state, king_square, opponent_color
        )

        # STEP 8: If any opposing piece can legally attack the king's square, reject
        if opponent_can_attack:
            return {
                'safe': False,
                'reason': f"Moving would leave the {color} king in check"
            }
        else:
            # STEP 9: Otherwise accept it
            return {
                'safe': True,
                'reason': f"Move does not leave the {color} king in check"
            }

    def _is_square_attacked_by_opponent(self, game_state, target_square, opponent_color):
        """
        Check if any opponent piece can attack the target square.

        Args:
            game_state (GameState): The game state to check
            target_square (str): The square to check for attacks (e.g., "e1")
            opponent_color (str): 'white' or 'black' (color of pieces doing the checking)

        Returns:
            bool: True if any opponent piece can attack the square, False otherwise
        """
        # Check all squares on the board for opponent pieces
        for row in range(8):
            for col in range(8):
                piece = game_state.board.get_piece_at(row, col)
                if piece is not None and piece.color == opponent_color:
                    # Check if this piece can attack the target square
                    from_square = coordinates_to_square(row, col)
                    if self._can_piece_attack_square(game_state, piece, from_square, target_square):
                        return True  # Found an attacker - OR condition satisfied

        return False  # No pieces can attack the square

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
        # (except king, which we treat normally here - king attack detection is rare)
        validator = self.attack_validators.get(piece.piece_type)
        if validator is None:
            return False

        # Use the piece's normal movement validator to check if it can move to target
        # This works for rook, bishop, knight, queen, king
        # Note: We don't check if the move would be legal in terms of turn/check etc.
        # We only check if the piece *could* move there according to its movement rules
        result = validator.validate(game_state.board, from_square, to_square)
        return result['valid']

    def _is_square_attacked_by_color(self, game_state, target_square, attacking_color):
        """
        Check if any piece of the given color can attack the target square.
        Reuses Layer 1 movement logic for attack detection.

        Args:
            game_state (GameState): The game state to check
            target_square (str): The target square to check for attacks
            attacking_color (str): 'white' or 'black' (color of pieces doing the attacking)

        Returns:
            bool: True if any piece of the given color can attack the square, False otherwise
        """
        # Check all squares on the board for pieces of the given color
        for row in range(8):
            for col in range(8):
                piece = game_state.board.get_piece_at(row, col)
                if piece is not None and piece.color == attacking_color:
                    # Check if this piece can attack the target square
                    from_square = coordinates_to_square(row, col)
                    if self._can_piece_attack_square(game_state, piece, from_square, target_square):
                        return True  # Found an attacker
        return False  # No pieces of the given color can attack the square

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


# Automata Theory Notes for Safety Filter (Layer 4):
# This layer demonstrates the computational concept of OR combination:
#
# GOAL: Determine if king is in check after a move
# METHOD: Check if ANY opponent piece can attack the king's square
#
# FORMALISM:
# King_in_check = Attack(piece1, king) OR Attack(piece2, king) OR ... OR Attack(pieceN, king)
#
# WHERE:
# - Attack(piece_i, king) is computed using Layer 1 movement logic
# - The OR operation combines results from all opponent pieces
#
# LAYER 4 RESPONSIBILITIES:
# 1. King location identification
# 2. Iterating over all opponent pieces
# 3. Reusing Layer 1 validators for attack computation
# 4. Applying OR logic to combine attack possibilities
# 5. Negating the result for safety decision (safe = NOT in_check)
#
# KEY INSIGHT: Layer 4 reuses Layer 1 instead of duplicating logic:
# - Instead of rewriting rook/bishop/etc. movement rules for attack detection
# - Layer 4 calls the same DFAs used for move validation
# - This demonstrates layered architecture and code reuse
#
# SPECIAL CASE HANDLING:
# - Pawns: Attack movement != normal movement (diagonal vs forward)
# - Kings: Rarely attack other kings in practice, but logic handles it
#
# This layer clearly shows how the safety filter computes:
# "Is there ANY way for the opponent to capture our king on their next turn?"
# Using Layer 1 movement logic combined with OR operations.