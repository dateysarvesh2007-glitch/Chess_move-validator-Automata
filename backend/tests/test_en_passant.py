"""
Regression tests for en passant validation.

Tests Layer 2 historical requirements, Layer 3 move sequencing,
and Layer 4 king-safety restrictions.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.layer2.en_passant import EnPassantValidator
from src.layer3.game_validator import GameValidator
from src.game_state import GameState
from src.board import Board
from src.piece import Piece


class TestEnPassant(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()
        self.validator = GameValidator(self.game_state)
        self.en_passant_validator = EnPassantValidator(self.game_state)

    def play_move(self, from_square, to_square):
        """Validate and execute a normal move."""
        result = self.validator.validate_move(from_square, to_square)

        self.assertTrue(
            result['accepted'],
            f"{from_square}-{to_square} should be legal: {result['reason']}"
        )

        self.game_state.make_move(from_square, to_square)
        return result

    def test_no_en_passant_initially(self):
        """No en passant opportunity exists at the start of a game."""
        self.assertIsNone(self.game_state.en_passant_target)

        result = self.validator.validate_move('e2', 'd3')

        self.assertFalse(result['accepted'])
        self.assertIn('en passant', result['reason'].lower())

    def test_white_en_passant_capture(self):
        """White can capture en passant after Black advances two squares."""
        self.play_move('e2', 'e4')
        self.play_move('a7', 'a6')
        self.play_move('e4', 'e5')
        self.play_move('d7', 'd5')

        self.assertEqual(self.game_state.en_passant_target, 'd6')

        result = self.validator.validate_move('e5', 'd6')

        self.assertTrue(result['accepted'], result['reason'])
        self.assertTrue(result.get('is_en_passant', False))

        # Validation must not modify the actual board.
        self.assertIsNotNone(self.game_state.board.get_piece('e5'))
        self.assertIsNotNone(self.game_state.board.get_piece('d5'))
        self.assertIsNone(self.game_state.board.get_piece('d6'))

        # Execute the accepted move.
        self.game_state.make_move('e5', 'd6')

        self.assertIsNone(self.game_state.board.get_piece('e5'))
        self.assertIsNone(self.game_state.board.get_piece('d5'))

        captured_pawn = self.game_state.board.get_piece('d6')

        self.assertIsNotNone(captured_pawn)
        self.assertEqual(captured_pawn.piece_type, 'pawn')
        self.assertEqual(captured_pawn.color, 'white')

        self.assertIsNone(self.game_state.en_passant_target)
        self.assertEqual(self.game_state.current_turn, 'black')

    def test_black_en_passant_capture(self):
        """Black can capture en passant after White advances two squares."""
        self.play_move('a2', 'a3')
        self.play_move('e7', 'e5')
        self.play_move('a3', 'a4')
        self.play_move('e5', 'e4')
        self.play_move('d2', 'd4')

        self.assertEqual(self.game_state.en_passant_target, 'd3')

        result = self.validator.validate_move('e4', 'd3')

        self.assertTrue(result['accepted'], result['reason'])
        self.assertTrue(result.get('is_en_passant', False))

        self.game_state.make_move('e4', 'd3')

        self.assertIsNone(self.game_state.board.get_piece('e4'))
        self.assertIsNone(self.game_state.board.get_piece('d4'))

        capturing_pawn = self.game_state.board.get_piece('d3')

        self.assertIsNotNone(capturing_pawn)
        self.assertEqual(capturing_pawn.piece_type, 'pawn')
        self.assertEqual(capturing_pawn.color, 'black')

        self.assertIsNone(self.game_state.en_passant_target)
        self.assertEqual(self.game_state.current_turn, 'white')

    def test_en_passant_opportunity_expires(self):
        """En passant is unavailable after the opponent makes another move."""
        self.play_move('e2', 'e4')
        self.play_move('a7', 'a6')
        self.play_move('e4', 'e5')
        self.play_move('d7', 'd5')

        self.assertEqual(self.game_state.en_passant_target, 'd6')

        self.play_move('g1', 'f3')

        self.assertIsNone(self.game_state.en_passant_target)

        self.play_move('a6', 'a5')

        result = self.validator.validate_move('e5', 'd6')

        self.assertFalse(result['accepted'])
        self.assertIn('en passant', result['reason'].lower())

    def test_en_passant_requires_previous_double_pawn_move(self):
        """A diagonal move to an empty square is not automatically en passant."""
        self.play_move('e2', 'e4')
        self.play_move('a7', 'a6')
        self.play_move('e4', 'e5')

        self.assertIsNone(self.game_state.en_passant_target)

        # Black must make a move so that it is White's turn again.
        # Black does not advance a pawn two squares.
        self.play_move('a6', 'a5')

        self.assertIsNone(self.game_state.en_passant_target)

        result = self.validator.validate_move('e5', 'd6')

        self.assertFalse(result['accepted'])
        self.assertIn('en passant', result['reason'].lower())

    def test_en_passant_wrong_destination(self):
        """The capturing pawn must move to the exact en passant target."""
        self.play_move('e2', 'e4')
        self.play_move('a7', 'a6')
        self.play_move('e4', 'e5')
        self.play_move('d7', 'd5')

        result = self.en_passant_validator.validate_en_passant(
            'white', 'e5', 'd5'
        )

        self.assertFalse(result['valid'])
        self.assertIn('must be to square', result['reason'].lower())

    def test_en_passant_must_be_diagonal(self):
        """En passant cannot be performed by moving straight forward."""
        self.play_move('e2', 'e4')
        self.play_move('a7', 'a6')
        self.play_move('e4', 'e5')
        self.play_move('d7', 'd5')

        result = self.en_passant_validator.validate_en_passant(
            'white', 'e5', 'e6'
        )

        self.assertFalse(result['valid'])

    def test_en_passant_cannot_expose_king_to_check(self):
        """
        Reject en passant if removing both pawns exposes the moving
        player's king to an opposing rook.
        """
        self.game_state.board = Board()
        self.game_state.current_turn = 'white'
        self.game_state.en_passant_target = 'd6'

        self.game_state.board.place_piece(
            Piece('king', 'white', 'e1'), 'e1'
        )

        self.game_state.board.place_piece(
            Piece('pawn', 'white', 'e5'), 'e5'
        )

        self.game_state.board.place_piece(
            Piece('pawn', 'black', 'd5'), 'd5'
        )

        self.game_state.board.place_piece(
            Piece('rook', 'black', 'e8'), 'e8'
        )

        self.game_state.board.place_piece(
            Piece('king', 'black', 'a8'), 'a8'
        )

        result = self.validator.validate_move('e5', 'd6')

        self.assertFalse(result['accepted'])
        self.assertTrue(result['reason'])

        # Rejected move must leave the original position untouched.
        self.assertIsNotNone(self.game_state.board.get_piece('e5'))
        self.assertIsNotNone(self.game_state.board.get_piece('d5'))
        self.assertIsNone(self.game_state.board.get_piece('d6'))

        self.assertEqual(self.game_state.current_turn, 'white')
        self.assertEqual(self.game_state.en_passant_target, 'd6')


if __name__ == '__main__':
    unittest.main()
