"""
Integration tests for the complete chess move validator.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.layer3.game_validator import GameValidator
from src.game_state import GameState


class TestGameSequence(unittest.TestCase):

    def setUp(self):
        self.game_state = GameState()
        self.validator = GameValidator(self.game_state)

    def test_initial_position(self):
        """Test that the game starts with 16 pieces per side."""
        white_pieces = 0
        black_pieces = 0

        for row in range(8):
            for col in range(8):
                piece = self.game_state.board.get_piece_at(row, col)

                if piece is not None:
                    if piece.color == 'white':
                        white_pieces += 1
                    else:
                        black_pieces += 1

        self.assertEqual(white_pieces, 16)
        self.assertEqual(black_pieces, 16)

    def test_legal_opening_moves(self):
        """Test basic legal opening moves."""
        result = self.validator.validate_move('e2', 'e4')
        self.assertTrue(result['accepted'], result['reason'])
        self.assertEqual(result['move_notation'], 'e4')

        self.game_state.make_move('e2', 'e4')

        result = self.validator.validate_move('e7', 'e5')
        self.assertTrue(result['accepted'], result['reason'])
        self.assertEqual(result['move_notation'], 'e5')

        self.game_state.make_move('e7', 'e5')

        result = self.validator.validate_move('g1', 'f3')
        self.assertTrue(result['accepted'], result['reason'])
        self.assertEqual(result['move_notation'], 'f3')

    def test_illegal_moves(self):
        """Test that illegal moves are properly rejected."""
        result = self.validator.validate_move('e2', 'e5')

        self.assertFalse(result['accepted'])
        self.assertIn('three squares', result['reason'].lower())

        self.game_state.make_move('e2', 'e4')

        result = self.validator.validate_move('e2', 'e3')
        self.assertFalse(result['accepted'])

        # Reset and verify that the pawn can move from its initial square.
        self.game_state = GameState()
        self.validator = GameValidator(self.game_state)

        result = self.validator.validate_move('e2', 'e3')
        self.assertTrue(result['accepted'], result['reason'])

        self.game_state.make_move('e2', 'e3')

        result = self.validator.validate_move('e2', 'e3')
        self.assertFalse(result['accepted'])
        self.assertIn('no piece at e2', result['reason'].lower())

    def test_turn_alternation(self):
        """Test that turns alternate after moves."""
        self.assertEqual(self.game_state.current_turn, 'white')

        result = self.validator.validate_move('e2', 'e4')
        self.assertTrue(result['accepted'])
        self.game_state.make_move('e2', 'e4')

        self.assertEqual(self.game_state.current_turn, 'black')

        result = self.validator.validate_move('e7', 'e5')
        self.assertTrue(result['accepted'])
        self.game_state.make_move('e7', 'e5')

        self.assertEqual(self.game_state.current_turn, 'white')

    def test_move_does_not_corrupt_state_on_rejection(self):
        """Illegal moves must not modify the game state."""
        initial_king_pos = self.game_state.get_king_position('white')

        result = self.validator.validate_move('e1', 'e3')
        self.assertFalse(result['accepted'])

        self.assertEqual(
            self.game_state.get_king_position('white'),
            initial_king_pos
        )
        self.assertEqual(self.game_state.current_turn, 'white')

    def test_simple_sequence(self):
        """Test a sequence of legal moves."""
        moves = [
            ('e2', 'e4', 'White pawn e2-e4'),
            ('e7', 'e5', 'Black pawn e7-e5'),
            ('g1', 'f3', 'White knight g1-f3'),
            ('f8', 'c5', 'Black bishop f8-c5'),
        ]

        for from_sq, to_sq, description in moves:
            with self.subTest(move=description):
                result = self.validator.validate_move(from_sq, to_sq)

                self.assertTrue(
                    result['accepted'],
                    f"{description} should be legal: {result['reason']}"
                )

                self.game_state.make_move(from_sq, to_sq)

    def test_check_detection(self):
        """Test that the validator has its check-safety components."""
        self.assertTrue(hasattr(self.validator, 'safety_filter'))
        self.assertTrue(
            hasattr(self.validator.safety_filter, 'is_move_safe')
        )


if __name__ == '__main__':
    unittest.main()
