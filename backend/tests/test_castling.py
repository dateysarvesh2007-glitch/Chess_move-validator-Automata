"""
Castling regression and integration tests.

Tests Layer 2 castling requirements and the complete
Layer 3 + Layer 4 castling validation process.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.layer2.castling import CastlingValidator
from src.layer3.game_validator import GameValidator
from src.game_state import GameState
from src.board import Board
from src.piece import Piece


class TestCastling(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()
        self.castling_validator = CastlingValidator(self.game_state)
        self.game_validator = GameValidator(self.game_state)

    def clear_castling_paths(self):
        """Clear all squares between kings and rooks."""
        squares = [
            'f1', 'g1', 'b1', 'c1', 'd1',
            'f8', 'g8', 'b8', 'c8', 'd8'
        ]

        for square in squares:
            self.game_state.board.remove_piece(square)

    def prepare_castling_position(self, color):
        """
        Create a minimal position containing the moving king,
        both of its rooks, and the opposing king.
        """
        self.game_state.board = Board()
        self.game_state.current_turn = color
        self.game_state.en_passant_target = None
        self.game_state.move_history = []

        if color == 'white':
            king_square = 'e1'
            opponent_king_square = 'a8'
            rook_squares = ['a1', 'h1']
        else:
            king_square = 'e8'
            opponent_king_square = 'a1'
            rook_squares = ['a8', 'h8']

        self.game_state.board.place_piece(
            Piece('king', color, king_square), king_square
        )

        self.game_state.board.place_piece(
            Piece('king',
                  'black' if color == 'white' else 'white',
                  opponent_king_square),
            opponent_king_square
        )

        for square in rook_squares:
            self.game_state.board.place_piece(
                Piece('rook', color, square), square
            )

        self.castling_validator = CastlingValidator(self.game_state)
        self.game_validator = GameValidator(self.game_state)

    def test_initial_castling_rights(self):
        """Rights exist initially, but pieces block actual castling."""
        for color in ('white', 'black'):
            for kingside in (True, False):
                side = 'kingside' if kingside else 'queenside'

                self.assertTrue(
                    self.game_state.castling_rights[color][side]
                )

                result = self.castling_validator.validate_castling(
                    color, kingside
                )

                self.assertFalse(result['valid'])
                self.assertIn('blocked', result['reason'].lower())

        self.clear_castling_paths()

        for color in ('white', 'black'):
            for kingside in (True, False):
                result = self.castling_validator.validate_castling(
                    color, kingside
                )

                self.assertTrue(
                    result['valid'],
                    f"{color} castling failed: {result['reason']}"
                )

    def test_losing_castling_rights_after_king_move(self):
        """Moving the king permanently removes both castling rights."""
        self.clear_castling_paths()

        self.game_state.board.remove_piece('e1')
        self.game_state.board.remove_piece('e2')

        white_king = Piece('king', 'white', 'e2')
        self.game_state.board.place_piece(white_king, 'e2')

        self.game_state.castling_rights['white']['kingside'] = False
        self.game_state.castling_rights['white']['queenside'] = False

        for kingside in (True, False):
            result = self.castling_validator.validate_castling(
                'white', kingside
            )
            self.assertFalse(result['valid'])

    def test_losing_castling_rights_after_rook_move(self):
        """Moving one rook removes only its corresponding right."""
        self.clear_castling_paths()

        self.game_state.board.remove_piece('h1')
        self.game_state.board.remove_piece('h2')

        white_rook = Piece('rook', 'white', 'h2')
        self.game_state.board.place_piece(white_rook, 'h2')

        self.game_state.castling_rights['white']['kingside'] = False

        result = self.castling_validator.validate_castling('white', True)
        self.assertFalse(result['valid'])

        result = self.castling_validator.validate_castling('white', False)
        self.assertTrue(
            result['valid'],
            f"Queenside should remain available: {result['reason']}"
        )

    def test_castling_path_blocking(self):
        """A piece on any required path square prevents castling."""
        self.game_state.board.remove_piece('f1')

        blocker = Piece('pawn', 'white', 'f1')
        self.game_state.board.place_piece(blocker, 'f1')

        result = self.castling_validator.validate_castling('white', True)

        self.assertFalse(result['valid'])
        self.assertIn('blocked', result['reason'].lower())

        self.game_state.board.remove_piece('f1')
        self.game_state.board.remove_piece('d1')

        blocker2 = Piece('pawn', 'white', 'd1')
        self.game_state.board.place_piece(blocker2, 'd1')

        result = self.castling_validator.validate_castling('white', False)

        self.assertFalse(result['valid'])
        self.assertIn('blocked', result['reason'].lower())

    def test_get_castling_move(self):
        """Verify the four castling move coordinate combinations."""
        self.clear_castling_paths()

        expected_moves = {
            ('white', True): ('e1', 'g1', 'h1', 'f1'),
            ('white', False): ('e1', 'c1', 'a1', 'd1'),
            ('black', True): ('e8', 'g8', 'h8', 'f8'),
            ('black', False): ('e8', 'c8', 'a8', 'd8'),
        }

        for key, expected in expected_moves.items():
            color, kingside = key

            result = self.castling_validator.get_castling_move(
                color, kingside
            )

            self.assertEqual(result, expected)

    def test_all_four_castling_moves_accepted_by_game_validator(self):
        """All four legal castling moves pass Layers 2, 3 and 4."""
        cases = [
            ('white', True, 'e1', 'g1', 'h1', 'f1'),
            ('white', False, 'e1', 'c1', 'a1', 'd1'),
            ('black', True, 'e8', 'g8', 'h8', 'f8'),
            ('black', False, 'e8', 'c8', 'a8', 'd8'),
        ]

        for color, kingside, king_from, king_to, rook_from, rook_to in cases:
            with self.subTest(color=color, kingside=kingside):
                self.prepare_castling_position(color)

                result = self.game_validator.validate_move(
                    king_from, king_to
                )

                self.assertTrue(
                    result['accepted'],
                    f"{color} castling failed: {result['reason']}"
                )
                self.assertTrue(result.get('is_castling'))
                self.assertEqual(result['kingside'], kingside)

                # Validation must not change the actual board.
                self.assertIsNotNone(
                    self.game_state.board.get_piece(king_from)
                )
                self.assertIsNotNone(
                    self.game_state.board.get_piece(rook_from)
                )
                self.assertIsNone(
                    self.game_state.board.get_piece(king_to)
                )
                self.assertIsNone(
                    self.game_state.board.get_piece(rook_to)
                )

                self.assertEqual(self.game_state.current_turn, color)

    def test_castling_while_in_check_is_rejected(self):
        """A king cannot castle while currently in check."""
        for color in ('white', 'black'):
            with self.subTest(color=color):
                self.prepare_castling_position(color)

                if color == 'white':
                    attacker_square = 'e8'
                    king_from, king_to = 'e1', 'g1'
                else:
                    attacker_square = 'e1'
                    king_from, king_to = 'e8', 'g8'

                opponent = 'black' if color == 'white' else 'white'

                self.game_state.board.place_piece(
                    Piece('rook', opponent, attacker_square),
                    attacker_square
                )

                result = self.game_validator.validate_move(
                    king_from, king_to
                )

                self.assertFalse(result['accepted'])
                self.assertIn('check', result['reason'].lower())

                self.assertIsNotNone(
                    self.game_state.board.get_piece(king_from)
                )
                self.assertEqual(self.game_state.current_turn, color)

    def test_castling_through_attacked_square_is_rejected(self):
        """A king cannot cross an attacked transit square."""
        self.prepare_castling_position('white')

        # Black rook attacks f1, the king's transit square.
        self.game_state.board.place_piece(
            Piece('rook', 'black', 'f8'), 'f8'
        )

        result = self.game_validator.validate_move('e1', 'g1')

        self.assertFalse(result['accepted'])
        self.assertIn('attacked square', result['reason'].lower())

        # Original position must remain unchanged.
        self.assertIsNotNone(self.game_state.board.get_piece('e1'))
        self.assertIsNotNone(self.game_state.board.get_piece('h1'))
        self.assertIsNone(self.game_state.board.get_piece('f1'))
        self.assertIsNone(self.game_state.board.get_piece('g1'))

    def test_castling_into_check_is_rejected(self):
        """A king cannot finish castling on an attacked destination."""
        self.prepare_castling_position('white')

        # Black rook attacks g1, the king's final square.
        self.game_state.board.place_piece(
            Piece('rook', 'black', 'g8'), 'g8'
        )

        result = self.game_validator.validate_move('e1', 'g1')

        self.assertFalse(result['accepted'])
        self.assertIn('check', result['reason'].lower())

        # Original position must remain unchanged.
        self.assertIsNotNone(self.game_state.board.get_piece('e1'))
        self.assertIsNotNone(self.game_state.board.get_piece('h1'))
        self.assertIsNone(self.game_state.board.get_piece('g1'))
        self.assertIsNone(self.game_state.board.get_piece('f1'))

    def test_queenside_castling_through_attacked_square_is_rejected(self):
        """Queenside castling cannot pass through an attacked d-file square."""
        self.prepare_castling_position('white')

        # Black rook attacks d1, the queenside transit square.
        self.game_state.board.place_piece(
            Piece('rook', 'black', 'd8'), 'd8'
        )

        result = self.game_validator.validate_move('e1', 'c1')

        self.assertFalse(result['accepted'])
        self.assertIn('attacked square', result['reason'].lower())

        self.assertIsNotNone(self.game_state.board.get_piece('e1'))
        self.assertIsNotNone(self.game_state.board.get_piece('a1'))
        self.assertIsNone(self.game_state.board.get_piece('c1'))
        self.assertIsNone(self.game_state.board.get_piece('d1'))


if __name__ == '__main__':
    unittest.main()
