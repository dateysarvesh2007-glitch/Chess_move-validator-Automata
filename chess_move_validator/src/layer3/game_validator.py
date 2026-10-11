"""
Game validator that coordinates move validation across all layers.
This demonstrates Layer 3 of the four-layer architecture.

The game validator orchestrates the validation process:
1. Determines whose turn it is
2. Parses/interprets the move
3. Validates basic movement using Layer 1 (piece-specific DFAs)
4. Validates history-dependent rules using Layer 2 (castling, en passant)
5. Applies/simulates the move temporarily
6. Checks king safety using Layer 4 (safety filter)
7. Accepts or rejects the move with explanations
8. Updates game state and switches turns if accepted

This layer treats chess moves as an ordered input sequence and
validates each move in turn.
"""

from piece import Piece
from layer1.rook import RookDFA
from layer1.bishop import BishopDFA
from layer1.knight import KnightDFA
from layer1.pawn import PawnDFA
from layer1.king import KingDFA
from layer1.queen import QueenDFA
from layer2.castling import CastlingValidator
from layer2.en_passant import EnPassantValidator
from layer4.safety_filter import SafetyFilter
from layer4.check_detector import CheckDetector
from game_state import GameState
from coordinates import square_to_coordinates, coordinates_to_square


class GameValidator:
    """
    Main game validator that coordinates all layers of move validation.
    """

    def __init__(self, game_state):
        """
        Initialize the game validator with all necessary components.

        Args:
            game_state (GameState): The current game state
        """
        self.game_state = game_state

        # Initialize Layer 1 validators (DFAs for each piece type)
        self.piece_validators = {
            'rook': RookDFA(),
            'bishop': BishopDFA(),
            'knight': KnightDFA(),
            'pawn': PawnDFA(),
            'king': KingDFA(),
            'queen': QueenDFA()
        }

        # Initialize Layer 2 validators (history-dependent)
        self.castling_validator = CastlingValidator(game_state)
        self.en_passant_validator = EnPassantValidator(game_state)

        # Initialize Layer 4 validators
        self.safety_filter = SafetyFilter(game_state)
        self.check_detector = CheckDetector(game_state)

    def validate_move(self, from_square, to_square):
        """
        Validate a chess move using all four layers.

        Args:
            from_square (str): Starting square (e.g., "e2")
            to_square (str): Destination square (e.g., "e4")

        Returns:
            dict: Validation result with keys:
                  - 'accepted': bool
                  - 'reason': str
                  - 'move_notation': str (e.g., "e4" or "e4+" for check)
                  - 'is_check': bool (whether move gives check)
                  - Additional move-specific info as needed
        """
        # Initialize result dictionary
        result = {
            'accepted': False,
            'reason': '',
            'move_notation': '',
            'is_check': False
        }

        # STEP 0: Basic input validation
        basic_validation = self._validate_basic_input(from_square, to_square)
        if not basic_validation['valid']:
            result['reason'] = basic_validation['reason']
            return result

        # STEP 1: Determine whose turn it is and get the piece
        current_color = self.game_state.current_turn
        piece = self.game_state.board.get_piece(from_square)

        # STEP 2: Check if there's a piece at the starting position
        # Let the Layer 1 validator handle this to get specific messages like "No pawn at starting position"

        # STEP 3: Check if it's the correct player's piece
        if piece is None:
            # No piece at starting position - let Layer 1 validator handle this
            pass
        elif piece.color != current_color:
            result['reason'] = f"The {from_square} piece belongs to {piece.color}, not {current_color}"
            return result

        # STEP 4: Validate basic movement using Layer 1 (piece-specific DFA)
        layer1_result = self._validate_layer1_movement(piece, from_square, to_square)
        if not layer1_result['valid']:
            result['reason'] = layer1_result['reason']
            return result

        # STEP 5: Validate history-dependent rules using Layer 2
        layer2_result = self._validate_layer2_rules(piece, from_square, to_square, current_color)
        if not layer2_result['valid']:
            result['reason'] = layer2_result['reason']
            return result

        # STEP 6: Check if the move is castling (special handling)
        if piece.piece_type == 'king':
            castling_result = self._validate_castling_move(piece, from_square, to_square, current_color)
            if castling_result['valid']:
                # Handle castling move execution
                return self._execute_castling(castling_result, current_color)
            # If not castling, continue with normal move validation

        # STEP 7: Apply/simulate the move temporarily
        temp_game_state = self.game_state.copy()
        move_record = temp_game_state.make_move(from_square, to_square)

        # STEP 8: Check king safety using Layer 4 (safety filter)
        safety_result = self.safety_filter.is_move_safe(temp_game_state, from_square, to_square, current_color)
        if not safety_result['safe']:
            result['reason'] = safety_result['reason']
            return result

        # STEP 9: Check if the move gives check (to be added to output)
        is_check = self._gives_check(temp_game_state, from_square, to_square, current_color)

        # STEP 10: Move is valid - prepare result (do NOT modify actual game state here)
        # The caller is responsible for making the move if they want to execute it
        result['accepted'] = True
        result['move_notation'] = to_square
        result['is_check'] = is_check

        if is_check:
            result['move_notation'] += '+'

        # Generate appropriate reason message
        result['reason'] = self._generate_accept_reason(piece, from_square, to_square, is_check)

        return result

    def _validate_basic_input(self, from_square, to_square):
        """Validate basic input format."""
        if not from_square or not to_square:
            return {'valid': False, 'reason': "Both source and destination squares must be specified"}

        try:
            square_to_coordinates(from_square)
            square_to_coordinates(to_square)
        except ValueError as e:
            return {'valid': False, 'reason': f"Invalid square format: {e}"}

        if from_square == to_square:
            return {'valid': False, 'reason': "Cannot move to the same square"}

        return {'valid': True}

    def _validate_layer1_movement(self, piece, from_square, to_square):
        """
        Validate basic movement using the appropriate Layer 1 DFA.

        Args:
            piece (Piece): The piece to move
            from_square (str): Starting square
            to_square (str): Destination square

        Returns:
            dict: Validation result from the piece's DFA
        """
        # Note: The validators themselves get the piece from the board using
        # board.get_piece(from_square), so they will work correctly even if
        # we pass None as the piece parameter

        validator = self.piece_validators.get(piece.piece_type if piece is not None else 'pawn')
        # Handle case where we can't determine piece type (when piece is None)
        # We'll default to 'pawn' but this might not be accurate for all cases
        # However, the validators will check the actual piece type on the board
        if validator is None:
            # If we still don't have a validator, try to determine from game context
            # or return a generic error
            if piece is None:
                # When there's no piece, we can't know what type to expect
                # Let's try to infer from the current turn what might be expected
                # but this is complex - for now, let's see if the validators can handle it
                return {'valid': False, 'reason': f"No piece at {from_square}"}
            return {'valid': False, 'reason': f"No validator for piece type: {piece.piece_type}"}

        return validator.validate(self.game_state.board, from_square, to_square)

    def _validate_layer2_rules(self, piece, from_square, to_square, color):
        """
        Validate history-dependent rules using Layer 2 validators.

        Args:
            piece (Piece): The piece to move
            from_square (str): Starting square
            to_square (str): Destination square
            color (str): 'white' or 'black'

        Returns:
            dict: Validation result
        """
        # Handle castling separately (king moves two squares horizontally)
        if piece.piece_type == 'king':
            start_col = square_to_coordinates(from_square)[1]
            end_col = square_to_coordinates(to_square)[1]
            if abs(end_col - start_col) == 2:  # Castling move
                return self.castling_validator.validate_castling(color, end_col > start_col)

        # Handle en passant (pawn diagonal move to en passant target)
        if piece.piece_type == 'pawn':
            start_col = square_to_coordinates(from_square)[1]
            end_col = square_to_coordinates(to_square)[1]
            if abs(end_col - start_col) == 1:  # Diagonal move
                # Check if destination is empty (en passant capture goes to empty square)
                target_piece = self.game_state.board.get_piece(to_square)
                if target_piece is None:  # Could be en passant
                    return self.en_passant_validator.validate_en_passant(color, from_square, to_square)

        # For all other moves, Layer 2 validation passes
        return {'valid': True, 'reason': "No history-dependent rules apply to this move"}

    def _validate_castling_move(self, piece, from_square, to_square, color):
        """
        Validate if a king move is actually a castling attempt.

        Args:
            piece (Piece): The king piece
            from_square (str): Starting square
            to_square (str): Destination square
            color (str): 'white' or 'black'

        Returns:
            dict: Validation result for castling
        """
        start_col = square_to_coordinates(from_square)[1]
        end_col = square_to_coordinates(to_square)[1]

        # King moving two squares horizontally indicates castling
        start_row, _ = square_to_coordinates(from_square)
        end_row, _ = square_to_coordinates(to_square)

        if abs(end_col - start_col) == 2 and start_row == end_row:
            # This is a castling attempt
            kingside = end_col > start_col  # True if kingside (king moves right)
            return self.castling_validator.validate_castling(color, kingside)

        # Not a castling move
        return {'valid': False}

    def _execute_castling(self, castling_result, color):
        """
        Execute a castling move after validation.

        Args:
            castling_result (dict): Result from castling validation
            color (str): 'white' or 'black'

        Returns:
            dict: Final validation result
        """
        if not castling_result['valid']:
            return {
                'accepted': False,
                'reason': castling_result['reason'],
                'move_notation': '',
                'is_check': False
            }

        # Get the castling moves
        castling_move = self.castling_validator.get_castling_move(
            color,
            castling_result.get('kingside', True)  # Default to kingside if not specified
        )

        if castling_move is None:
            return {
                'accepted': False,
                'reason': "Unable to determine castling moves",
                'move_notation': '',
                'is_check': False
            }

        king_from, king_to, rook_from, rook_to = castling_move

        # Execute the king move
        self.game_state.make_move(king_from, king_to)
        # Execute the rook move
        self.game_state.make_move(rook_from, rook_to)

        # Determine if castling gives check (unlikely but possible)
        is_check = self._gives_check(self.game_state, king_from, king_to, color)

        # Prepare result
        result = {
            'accepted': True,
            'reason': castling_result['reason'],
            'move_notation': king_to + ('+' if is_check else ''),
            'is_check': is_check
        }

        # Add castling notation to reason if desired
        castle_type = "kingside" if castling_result.get('kingside', True) else "queenside"
        result['reason'] = f"Legal {castle_type} castling. {castling_result['reason']}"

        return result

    def _gives_check(self, game_state, from_square, to_square, color):
        """
        Check if a move gives check to the opponent.

        Args:
            game_state (GameState): The game state after the move
            from_square (str): Starting square
            to_square (str): Destination square
            color (str): 'white' or 'black' (color of the moving piece)

        Returns:
            bool: True if the move gives check, False otherwise
        """
        # Use the check detector to determine if this move gives check
        return self.check_detector.is_check(game_state, from_square, to_square, color)

    def _generate_accept_reason(self, piece, from_square, to_square, is_check):
        """
        Generate an appropriate acceptance reason message.

        Args:
            piece (Piece): The piece that moved
            from_square (str): Starting square
            to_square (str): Destination square
            is_check (bool): Whether the move gives check

        Returns:
            str: Reason for accepting the move
        """
        base_reasons = {
            'pawn': self._get_pawn_move_reason(from_square, to_square),
            'rook': f"Legal rook move from {from_square} to {to_square}",
            'knight': f"Legal knight move from {from_square} to {to_square}",
            'bishop': f"Legal bishop move from {from_square} to {to_square}",
            'queen': f"Legal queen move from {from_square} to {to_square}",
            'king': f"Legal king move from {from_square} to {to_square}"
        }

        base_reason = base_reasons.get(piece.piece_type, f"Legal {piece.piece_type} move")

        if is_check:
            return f"{base_reason}; opponent king is in check"
        else:
            return base_reason

    def parse_and_validate_algebraic_move(self, move_str):
        """
        Parse and validate a move in algebraic notation.

        This method provides a higher-level interface that accepts standard
        chess algebraic notation (e.g., "e4", "Nf3", "Be6", "O-O", "exd5",
        "Nbd2", etc.) and handles disambiguation when multiple pieces of
        the same type could move to the target square.

        Args:
            move_str (str): Move in algebraic notation (e.g., "e4", "Nf3")

        Returns:
            dict: Validation result with same format as validate_move()
        """
        # Handle castling
        if move_str == "O-O":
            return self._handle_castling('kingside')
        elif move_str == "O-O-O":
            return self._handle_castling('queenside')

        # Initialize result
        result = {
            'accepted': False,
            'reason': '',
            'move_notation': '',
            'is_check': False
        }

        # Parse the move string
        parsed = self._parse_algebraic_notation(move_str)
        if not parsed['valid']:
            result['reason'] = parsed['reason']
            return result

        piece_type = parsed['piece_type']  # 'pawn', 'knight', 'bishop', etc.
        target_square = parsed['target_square']
        disambiguation = parsed['disambiguation']  # dict with 'file' and/or 'rank'
        is_capture = parsed['is_capture']

        # Determine whose turn it is
        current_color = self.game_state.current_turn

        # Find all pieces of the current player's color that match the piece type
        candidate_pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.game_state.board.get_piece_at(row, col)
                if piece and piece.color == current_color and piece.piece_type == piece_type:
                    # Check disambiguation constraints
                    square = coordinates_to_square(row, col)
                    if self._matches_disambiguation(square, disambiguation):
                        candidate_pieces.append((piece, square))

        # If no candidates found, invalid move
        if not candidate_pieces:
            result['reason'] = f"No {piece_type} that can move to {target_square}"
            return result

        # Try each candidate piece to see if it can legally move to target_square
        valid_moves = []
        for piece, from_square in candidate_pieces:
            # Use existing validation logic
            move_result = self.validate_move(from_square, target_square)
            if move_result['accepted']:
                valid_moves.append((piece, from_square, move_result))

        # Handle results
        if not valid_moves:
            # No legal moves found
            if len(candidate_pieces) == 1:
                piece, from_square = candidate_pieces[0]
                # Try to get more specific reason from the validation
                temp_result = self.validate_move(from_square, target_square)
                result['reason'] = temp_result['reason']
            else:
                result['reason'] = f"No legal {piece_type} move to {target_square}"
            return result

        if len(valid_moves) == 1:
            # Exactly one valid move - accept it
            piece, from_square, move_result = valid_moves[0]
            # Actually make the move in the game state
            self.game_state.make_move(from_square, target_square)

            # Build result
            result['accepted'] = True
            result['reason'] = move_result['reason']
            result['move_notation'] = target_square
            result['is_check'] = move_result['is_check']

            if result['is_check']:
                result['move_notation'] += '+'

            return result

        # Multiple valid moves - this should not happen with proper disambiguation
        # but if it does, we need more specific disambiguation
        result['reason'] = f"Ambiguous move: multiple {piece_type}s can move to {target_square}"
        return result

    def _parse_algebraic_notation(self, move_str):
        """
        Parse algebraic notation into components.

        Args:
            move_str (str): Move string (e.g., "Nf3", "Be6", "exd5", "O-O")

        Returns:
            dict: Parsed components or error
        """
        # Handle special cases first
        if move_str in ["O-O", "O-O-O"]:
            return {'valid': True, 'special': 'castling'}

        # Initialize result
        result = {
            'valid': True,
            'piece_type': 'pawn',  # default
            'target_square': None,
            'disambiguation': {},  # {'file': 'b', 'rank': '3'}
            'is_capture': False,
            'promotion': None
        }

        i = 0
        length = len(move_str)

        # Check if it's a pawn move (no piece letter) or piece move
        if move_str[0] in 'NBKRQ':  # Piece move (K=king, Q=queen, R=rook, B=bishop, N=knight)
            piece_map = {'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen', 'K': 'king'}
            result['piece_type'] = piece_map[move_str[0]]
            i = 1
        elif move_str[0] in 'abcdefgh' and length >= 2 and move_str[1] == '=':
            # Pawn promotion like "a8=Q", "b8=Q", etc.
            result['piece_type'] = 'pawn'
            # Will handle promotion separately
            i = 0
        else:
            # Pawn move (starts with file letter a-h)
            result['piece_type'] = 'pawn'
            i = 0

        # Check for disambiguation (file or rank)
        # Pattern: [Piece][file/digit][file/digit][x?][to_square][=promotion][+/#]?
        # Examples: Nf3, Nbd2, N1f3, Ng5f3, exd5

        # Look for 'x' indicating capture
        if 'x' in move_str:
            result['is_capture'] = True
            move_str = move_str.replace('x', '')  # Remove for easier parsing

        # Extract target square (last 2 characters should be like "e4", "f7", etc.)
        # But need to account for promotion and check/checkmate symbols
        target_start = None
        for j in range(length - 1, -1, -1):
            if j + 1 < length and move_str[j] in 'abcdefgh' and move_str[j+1] in '12345678':
                target_start = j
                break

        if target_start is None:
            result['valid'] = False
            result['reason'] = f"Invalid move format: {move_str}"
            return result

        result['target_square'] = move_str[target_start:target_start+2]

        # Check for promotion
        if '=' in move_str:
            eq_pos = move_str.index('=')
            if eq_pos + 1 < length:
                promo_piece = move_str[eq_pos + 1]
                if promo_piece in 'NRBQ':  # Can't promote to king or pawn
                    promo_map = {'N': 'knight', 'R': 'rook', 'B': 'bishop', 'Q': 'queen'}
                    result['promotion'] = promo_map[promo_piece]
                else:
                    result['valid'] = False
                    result['reason'] = f"Invalid promotion piece: {promo_piece}"
                    return result

        # The part before the target square contains piece ID and disambiguation
        prefix = move_str[:target_start]

        # Parse disambiguation from prefix (skip piece letter if present)
        prefix_start = 1 if move_str[0] in 'NBKRQ' else 0
        disamb_str = move_str[prefix_start:target_start]

        # Process disambiguation string (could be file, rank, or both)
        for char in disamb_str:
            if char in 'abcdefgh':
                result['disambiguation']['file'] = char
            elif char in '12345678':
                result['disambiguation']['rank'] = char
            # Ignore other characters for now

        return result

    def _matches_disambiguation(self, square, disambiguation):
        """
        Check if a square matches disambiguation constraints.

        Args:
            square (str): Square like "e4"
            disambiguation (dict): Constraints like {'file': 'b'} or {'rank': '3'}

        Returns:
            bool: True if square matches constraints
        """
        if not disambiguation:
            return True

        file, rank = square[0], square[1]

        if 'file' in disambiguation and file != disambiguation['file']:
            return False
        if 'rank' in disambiguation and rank != disambiguation['rank']:
            return False

        return True

    def _handle_castling(self, kingside):
        """
        Handle castling move.

        Args:
            kingside (bool): True for kingside, False for queenside

        Returns:
            dict: Validation result
        """
        current_color = self.game_state.current_turn

        # Use existing castling validation
        castling_result = self.castling_validator.validate_castling(current_color, kingside)
        if not castling_result['valid']:
            return {
                'accepted': False,
                'reason': castling_result['reason'],
                'move_notation': '',
                'is_check': False
            }

        # Get the castling moves
        castling_move = self.castling_validator.get_castling_move(current_color, kingside)
        if castling_move is None:
            return {
                'accepted': False,
                'reason': "Unable to determine castling moves",
                'move_notation': '',
                'is_check': False
            }

        king_from, king_to, rook_from, rook_to = castling_move

        # Execute the king move
        self.game_state.make_move(king_from, king_to)
        # Execute the rook move
        self.game_state.make_move(rook_from, rook_to)

        # Determine if castling gives check
        is_check = self._gives_check(self.game_state, king_from, king_to, current_color)

        # Prepare result
        result = {
            'accepted': True,
            'reason': castling_result['reason'],
            'move_notation': king_to + ('+' if is_check else ''),
            'is_check': is_check
        }

        # Add castling notation to reason if desired
        castle_type = "kingside" if kingside else "queenside"
        result['reason'] = f"Legal {castle_type} castling. {castling_result['reason']}"

        return result

    def _get_pawn_move_reason(self, from_square, to_square):
        """Generate specific reason for pawn moves."""
        start_row, start_col = square_to_coordinates(from_square)
        end_row, end_col = square_to_coordinates(to_square)

        delta_row = end_row - start_row
        delta_col = end_col - start_col

        # Get piece color to determine direction
        piece = self.game_state.board.get_piece(from_square)
        if piece is None:
            return "Legal pawn move"

        is_white = piece.color == 'white'
        direction = 1 if is_white else -1

        if abs(delta_col) == 0 and abs(delta_row) == 1:
            return "Legal one-square pawn advance"
        elif abs(delta_col) == 0 and abs(delta_row) == 2:
            return "Legal two-square pawn advance from starting rank"
        elif abs(delta_col) == 1 and abs(delta_row) == 1:
            # Check if it was a capture
            target_piece = self.game_state.board.get_piece(to_square)
            if target_piece is not None and target_piece.color != piece.color:
                return "Legal pawn capture"
            else:
                # This would be en passant (handled elsewhere)
                return "Legal en passant capture"
        else:
            return "Legal pawn move"


# Automata Theory Notes for Game Validator (Layer 3):
# This layer demonstrates sequencing and coordination:
#
# INPUT: An ordered sequence of chess moves (each move is an input symbol)
#
# PROCESS: For each move in the sequence:
#   1. Layer 1: Validate basic piece movement (DFA)
#   2. Layer 2: Validate history-dependent rules (FSM)
#   3. Layer 3: Apply move, update turn, maintain sequence order
#   4. Layer 4: Validate king safety (check detection)
#
# LAYER 3 RESPONSIBILITIES:
# - Turn management (white/black alternation)
# - Move sequencing (processing moves in order)
# - Game state updates (applying valid moves)
# - Coordination between layers (calling Layers 1, 2, 4 in correct order)
#
# This shows how Layer 3 treats the game as a sequence processing problem:
# Each move is validated in the context of the current game state,
# and valid moves update the state for the next move in the sequence.
#
# The validator stops processing when it encounters an invalid move,
# demonstrating sequence rejection based on early termination.