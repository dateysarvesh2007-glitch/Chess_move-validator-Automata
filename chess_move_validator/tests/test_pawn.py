"""
Tests for the Pawn DFA movement validator.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from layer1.pawn import PawnDFA
from board import Board
from piece import Piece


class TestPawnDFA(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.pawn_dfa = PawnDFA()
        self.board = Board()

        # Set up a basic board with pawns for testing
        self.white_pawn = Piece('pawn', 'white', 'e2')
        self.black_pawn = Piece('pawn', 'black', 'e7')
        self.board.place_piece(self.white_pawn, 'e2')
        self.board.place_piece(self.black_pawn, 'e7')

    def test_pawn_dfa_initialization(self):
        """Test that the pawn DFA initializes correctly."""
        self.assertIsInstance(self.pawn_dfa, PawnDFA)

    def test_white_pawn_one_step(self):
        """Test white pawn one-step moves."""
        # From e2, white pawn can go to e3
        test_cases = [
            ('e2', 'e3', True),  # One step forward
            ('e2', 'e4', True),  # Two steps from start
            ('e2', 'e5', False), # Three steps (illegal)
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.pawn_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"White pawn move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_black_pawn_one_step(self):
        """Test black pawn one-step moves."""
        # From e7, black pawn can go to e6
        # Clear the board and set up black pawn
        self.board.remove_piece('e2')  # Remove white pawn
        self.board.remove_piece('e7')  # Remove black pawn
        black_pawn = Piece('pawn', 'black', 'e7')
        self.board.place_piece(black_pawn, 'e7')

        test_cases = [
            ('e7', 'e6', True),  # One step forward
            ('e7', 'e5', True),  # Two steps from start
            ('e7', 'e4', False), # Three steps (illegal)
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.pawn_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Black pawn move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_pawn_cannot_move_backwards(self):
        """Test that pawns cannot move backwards."""
        test_cases = [
            ('e2', 'e1', False),  # White pawn moving down
            ('e7', 'e8', False),  # Black pawn moving up
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.pawn_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Pawn move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")
                if not expected:
                    self.assertIn("forward", result['reason'].lower())

    def test_pawn_two_step_only_from_start(self):
        """Test that pawns can only move two steps from starting position."""
        # White pawn tests
        test_cases = [
            ('e2', 'e4', True),  # From start (rank 2) - two steps
            ('e3', 'e5', False), # From rank 3 - two steps (illegal)
            ('e4', 'e6', False), # From rank 4 - two steps (illegal)
        ]

        for from_sq, to_sq, expected in test_cases:
            # Clear board and set up pawn at from_sq
            self.board.remove_piece('e2')  # Remove white pawn if exists
            self.board.remove_piece('e3')  # Remove black pawn if exists
            white_pawn = Piece('pawn', 'white', from_sq)
            self.board.place_piece(white_pawn, from_sq)

            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.pawn_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"White pawn move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

        # Black pawn tests
        test_cases = [
            ('e7', 'e5', True),  # From start (rank 7) - two steps
            ('e6', 'e4', False), # From rank 6 - two steps (illegal)
            ('e5', 'e3', False), # From rank 5 - two steps (illegal)
        ]

        for from_sq, to_sq, expected in test_cases:
            # Clear board and set up pawn at from_sq
            self.board.remove_piece('e7')  # Remove white pawn if exists
            self.board.remove_piece('e6')  # Remove black pawn if exists
            black_pawn = Piece('pawn', 'black', from_sq)
            self.board.place_piece(black_pawn, from_sq)

            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.pawn_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Black pawn move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_pawn_diagonal_capture(self):
        """Test that pawns can capture diagonally."""
        # Set up white pawn at e4, black pawn at d5 (diagonal)
        self.board.remove_piece('e4')  # Remove white pawn if exists
        self.board.remove_piece('d5')  # Remove black pawn if exists
        white_pawn = Piece('pawn', 'white', 'e4')
        black_pawn = Piece('pawn', 'black', 'd5')
        self.board.place_piece(white_pawn, 'e4')
        self.board.place_piece(black_pawn, 'd5')

        # White pawn should be able to capture black pawn diagonally
        # White pawn at e4 captures to d5 or f5 (file +/-1, rank +1)
        result = self.pawn_dfa.validate(self.board, 'e4', 'd5')
        self.assertTrue(result['valid'],
                       "White pawn should be able to capture diagonally")
        self.assertIn("capture", result['reason'].lower())

        # Set up black pawn at e4, white pawn at d3 (diagonal)
        self.board.remove_piece('d5')  # Remove white pawn if exists
        self.board.remove_piece('e4')  # Remove black pawn if exists
        white_pawn = Piece('pawn', 'white', 'd3')
        black_pawn = Piece('pawn', 'black', 'e4')
        self.board.place_piece(white_pawn, 'd3')
        self.board.place_piece(black_pawn, 'e4')

        # Black pawn should be able to capture white pawn diagonally
        # Black pawn at e4 captures to d3 or f3 (file +/-1, rank -1)
        result = self.pawn_dfa.validate(self.board, 'e4', 'd3')
        self.assertTrue(result['valid'],
                       "Black pawn should be able to capture diagonally")
        self.assertIn("capture", result['reason'].lower())

    def test_pawn_cannot_move_diagonally_without_capture(self):
        """Test that pawns cannot move diagonally unless capturing."""
        # Set up white pawn at e4, but make sure d5 is empty (no piece to capture)
        self.board.remove_piece('e4')  # Clear e4 first
        self.board.remove_piece('d5')  # Clear d5
        white_pawn = Piece('pawn', 'white', 'e4')
        self.board.place_piece(white_pawn, 'e4')
        # d5 is intentionally left empty

        result = self.pawn_dfa.validate(self.board, 'e4', 'd5')
        self.assertFalse(result['valid'],
                       "Pawn should not be able to move diagonally without capturing")
        self.assertIn("capture", result['reason'].lower())

    def test_blocked_pawn(self):
        """Test that blocked pawns cannot move forward."""
        # White pawn at e2, blocking piece at e3
        self.board.remove_piece('e2')  # Remove white pawn if exists
        self.board.remove_piece('e3')  # Remove blocking piece if exists
        white_pawn = Piece('pawn', 'white', 'e2')
        blocking_piece = Piece('pawn', 'white', 'e3')  # Friendly piece blocking
        self.board.place_piece(white_pawn, 'e2')
        self.board.place_piece(blocking_piece, 'e3')

        # Should not be able to move forward because blocked
        result = self.pawn_dfa.validate(self.board, 'e2', 'e3')
        self.assertFalse(result['valid'],
                       "Pawn should not be able to move onto occupied square")
        self.assertIn("occupied", result['reason'].lower())

        # Should not be able to move two steps because first step is blocked
        result = self.pawn_dfa.validate(self.board, 'e2', 'e4')
        self.assertFalse(result['valid'],
                       "Pawn should not be able to move two steps when first step is blocked")
        self.assertIn("blocked", result['reason'].lower())

    def test_same_square_rejected(self):
        """Test that moving to the same square is rejected."""
        result = self.pawn_dfa.validate(self.board, 'e2', 'e2')
        self.assertFalse(result['valid'])
        self.assertIn("same square", result['reason'].lower())

    def test_no_piece_at_start(self):
        """Test that moves are rejected when there's no pawn at start."""
        # Clear the e2 square
        self.board.remove_piece('e2')

        result = self.pawn_dfa.validate(self.board, 'e2', 'e3')
        self.assertFalse(result['valid'])
        self.assertIn("No pawn", result['reason'])

    def test_wrong_piece_type(self):
        """Test that moves are rejected when the wrong piece type is at start."""
        # Put a rook at e2 instead of a pawn
        self.board.remove_piece('e2')
        rook = Piece('rook', 'white', 'e2')
        self.board.place_piece(rook, 'e2')

        result = self.pawn_dfa.validate(self.board, 'e2', 'e3')
        self.assertFalse(result['valid'])
        self.assertIn("No pawn", result['reason'])


if __name__ == '__main__':
    unittest.main()