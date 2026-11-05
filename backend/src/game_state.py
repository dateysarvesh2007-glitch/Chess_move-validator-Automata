"""
Game state management for chess.
Tracks the board, turn order, castling rights, en passant possibilities, and move history.
"""

from board import Board
from piece import Piece
from coordinates import square_to_coordinates, coordinates_to_square


class GameState:
    """
    Represents the complete state of a chess game.

    Attributes:
        board (Board): The chess board with piece positions
        current_turn (str): 'white' or 'black' indicating whose turn it is
        castling_rights (dict): Tracks castling availability for both sides
        en_passant_target (str or None): Square where en passant capture is possible, or None
        move_history (list): List of moves made in the game
    """

    def __init__(self):
        """Initialize a new game state with the standard starting position."""
        self.board = Board()
        self.current_turn = 'white'  # White always starts
        self.castling_rights = {
            'white': {'kingside': True, 'queenside': True},
            'black': {'kingside': True, 'queenside': True}
        }
        self.en_passant_target = None
        self.move_history = []

        # Set up the initial position
        self._setup_initial_position()

    def _setup_initial_position(self):
        """Set up the standard chess starting position."""
        # Place white pieces
        self.board.place_piece(Piece('rook', 'white', 'a1'), 'a1')
        self.board.place_piece(Piece('knight', 'white', 'b1'), 'b1')
        self.board.place_piece(Piece('bishop', 'white', 'c1'), 'c1')
        self.board.place_piece(Piece('queen', 'white', 'd1'), 'd1')
        self.board.place_piece(Piece('king', 'white', 'e1'), 'e1')
        self.board.place_piece(Piece('bishop', 'white', 'f1'), 'f1')
        self.board.place_piece(Piece('knight', 'white', 'g1'), 'g1')
        self.board.place_piece(Piece('rook', 'white', 'h1'), 'h1')

        # Place white pawns
        for file in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            self.board.place_piece(Piece('pawn', 'white', f'{file}2'), f'{file}2')

        # Place black pieces
        self.board.place_piece(Piece('rook', 'black', 'a8'), 'a8')
        self.board.place_piece(Piece('knight', 'black', 'b8'), 'b8')
        self.board.place_piece(Piece('bishop', 'black', 'c8'), 'c8')
        self.board.place_piece(Piece('queen', 'black', 'd8'), 'd8')
        self.board.place_piece(Piece('king', 'black', 'e8'), 'e8')
        self.board.place_piece(Piece('bishop', 'black', 'f8'), 'f8')
        self.board.place_piece(Piece('knight', 'black', 'g8'), 'g8')
        self.board.place_piece(Piece('rook', 'black', 'h8'), 'h8')

        # Place black pawns
        for file in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            self.board.place_piece(Piece('pawn', 'black', f'{file}7'), f'{file}7')

    def make_move(self, from_square, to_square):
        """
        Execute a move on the board (assuming it's already validated).

        Args:
            from_square (str): Starting square (e.g., "e2")
            to_square (str): Destination square (e.g., "e4")

        Returns:
            dict: Information about the move including captured piece, promotion, etc.
        """
        from_piece = self.board.get_piece(from_square)
        captured_piece = self.board.get_piece(to_square)

        # Handle en passant capture
        is_en_passant = False
        if (from_piece and from_piece.piece_type == 'pawn' and
            to_square == self.en_passant_target and captured_piece is None):
            # En passant capture - the captured pawn is on the same file, previous rank
            captured_piece = self.board.get_piece(f"{to_square[0]}{int(from_square[1])}")
            is_en_passant = True

        # Handle pawn promotion
        promotion_piece = None
        is_promotion = False
        if from_piece and from_piece.piece_type == 'pawn':
            # Check if pawn reaches the last rank
            to_rank = int(to_square[1])
            if (from_piece.color == 'white' and to_rank == 8) or \
               (from_piece.color == 'black' and to_rank == 1):
                is_promotion = True
                # Default to queen promotion (can be made configurable)
                promotion_piece = Piece('queen', from_piece.color, to_square)

        # Execute the move
        self.board.remove_piece(from_square)

        if is_en_passant:
            # Remove the captured pawn (which is on the same file as to_square, but from's rank)
            captured_square = f"{to_square[0]}{from_square[1]}"
            self.board.remove_piece(captured_square)

        # Place the moving piece (or promotion piece) on the destination
        if is_promotion and promotion_piece:
            self.board.place_piece(promotion_piece, to_square)
            # Update the piece's position for reference
            promotion_piece.position = to_square
            moved_piece = promotion_piece
        else:
            # Safety check: ensure we have a piece to move
            if from_piece is None:
                raise ValueError(f"No piece found at {from_square} to move")
            self.board.place_piece(from_piece, to_square)
            # Update the piece's position
            from_piece.position = to_square
            moved_piece = from_piece

        # Update castling rights if king or rook moved
        self._update_castling_rights(from_square, to_square, moved_piece)

        # Update en passant target
        self._update_en_passant_target(from_square, to_square, moved_piece, captured_piece)

        # Record the move
        move_record = {
            'from': from_square,
            'to': to_square,
            'piece': moved_piece.piece_type if moved_piece else None,
            'color': moved_piece.color if moved_piece else None,
            'captured': captured_piece.piece_type if captured_piece else None,
            'is_capture': captured_piece is not None or is_en_passant,
            'is_en_passant': is_en_passant,
            'is_promotion': is_promotion,
            'promotion_piece': promotion_piece.piece_type if promotion_piece else None
        }
        self.move_history.append(move_record)

        # Switch turns
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        return move_record

    def _update_castling_rights(self, from_square, to_square, moved_piece):
        """
        Update castling rights based on king or rook movement.

        Args:
            from_square (str): Starting square
            to_square (str): Destination square
            moved_piece (Piece): The piece that was moved
        """
        if not moved_piece:
            return

        # If king moves, lose both castling rights for that color
        if moved_piece.piece_type == 'king':
            self.castling_rights[moved_piece.color]['kingside'] = False
            self.castling_rights[moved_piece.color]['queenside'] = False

        # If rook moves, lose castling rights on that side for that color
        elif moved_piece.piece_type == 'rook':
            # Determine which rook based on starting position
            from_file = from_square[0]
            if moved_piece.color == 'white':
                if from_square == 'a1':
                    self.castling_rights['white']['queenside'] = False
                elif from_square == 'h1':
                    self.castling_rights['white']['kingside'] = False
            else:  # black
                if from_square == 'a8':
                    self.castling_rights['black']['queenside'] = False
                elif from_square == 'h8':
                    self.castling_rights['black']['kingside'] = False

    def _update_en_passant_target(self, from_square, to_square, moved_piece, captured_piece):
        """
        Update en passant target based on pawn movement.

        Args:
            from_square (str): Starting square
            to_square (str): Destination square
            moved_piece (Piece): The piece that was moved
            captured_piece (Piece): The piece that was captured (if any)
        """
        # Reset en passant target
        self.en_passant_target = None

        # Only pawns can create en passant opportunities
        if not moved_piece or moved_piece.piece_type != 'pawn':
            return

        # Check if this was a two-square pawn advance
        from_rank = int(from_square[1])
        to_rank = int(to_square[1])

        if abs(to_rank - from_rank) == 2:
            # This pawn just moved two squares - set en passant target
            # The target is the square skipped over
            middle_rank = (from_rank + to_rank) // 2
            self.en_passant_target = f"{from_square[0]}{middle_rank}"

    def copy(self):
        """
        Create a deep copy of the game state.

        Returns:
            GameState: A new GameState instance with the same state
        """
        new_state = GameState()
        new_state.board = self.board.copy()
        new_state.current_turn = self.current_turn
        new_state.castling_rights = {
            color: rights.copy() for color, rights in self.castling_rights.items()
        }
        new_state.en_passant_target = self.en_passant_target
        new_state.move_history = self.move_history.copy()
        return new_state

    def get_king_position(self, color):
        """
        Find the position of the king of the specified color.

        Args:
            color (str): 'white' or 'black'

        Returns:
            str: The square where the king is located (e.g., "e1"), or None if not found
        """
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if piece and piece.piece_type == 'king' and piece.color == color:
                    return coordinates_to_square(row, col)
        return None

    def is_square_attacked(self, square, attacking_color):
        """
        Check if a square is attacked by any piece of the specified color.

        Args:
            square (str): The square to check for attacks (e.g., "e1")
            attacking_color (str): The color of pieces doing the attacking ('white' or 'black')

        Returns:
            bool: True if the square is attacked by the specified color, False otherwise
        """
        # Check all squares on the board for pieces of the given color
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece_at(row, col)
                if piece is not None and piece.color == attacking_color:
                    # Check if this piece can attack the target square
                    from_square = coordinates_to_square(row, col)
                    if self._can_piece_attack_square(piece, from_square, square):
                        return True  # Found an attacker
        return False  # No pieces of the given color can attack the square

    def _can_piece_attack_square(self, piece, from_square, to_square):
        """
        Check if a specific piece can attack a target square.
        Reuses Layer 1 movement logic but accounts for piece-specific attack patterns.

        Args:
            piece (Piece): The piece that might be attacking
            from_square (str): Starting square of the piece
            to_square (str): Target square to check

        Returns:
            bool: True if the piece can attack the square, False otherwise
        """
        # Special handling for pawns: attack squares are different from movement squares
        if piece.piece_type == 'pawn':
            return self._can_pawn_attack_square(piece, from_square, to_square)

        # For all other pieces, attack movement is the same as normal movement
        # (except king, which we treat normally here - king attack detection is rare)
        from layer1.rook import RookDFA
        from layer1.bishop import BishopDFA
        from layer1.knight import KnightDFA
        from layer1.king import KingDFA
        from layer1.queen import QueenDFA

        attack_validators = {
            'rook': RookDFA(),
            'bishop': BishopDFA(),
            'knight': KnightDFA(),
            'pawn': PawnDFA(),  # Note: pawn attack movement is different from normal movement
            'king': KingDFA(),
            'queen': QueenDFA()
        }

        validator = attack_validators.get(piece.piece_type)
        if validator is None:
            return False

        # Use the piece's normal movement validator to check if it can move to target
        # This works for rook, bishop, knight, queen, king
        # Note: We don't check if the move would be legal in terms of turn/check etc.
        # We only check if the piece *could* move there according to its movement rules
        result = validator.validate(self.board, from_square, to_square)
        return result['valid']

    def _can_pawn_attack_square(self, piece, from_square, to_square):
        """
        Check if a pawn can attack a target square.
        Pawns attack diagonally forward, not straight ahead.

        Args:
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


# Automata Theory Notes for GameState:
# The GameState represents the mutable state that Layer 2 (history-dependent FSM)
# operates on. Unlike the DFAs in Layer 1 which only need current board state,
# the FSM in Layer 2 requires access to historical information like castling
# rights and en passant targets, which are stored in this class.