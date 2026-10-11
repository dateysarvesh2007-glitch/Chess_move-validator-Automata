"""
Tests for the Rook DFA movement validator.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from layer1.rook import RookDFA
from board import Board
from piece import Piece


class TestRookDFA(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.rook_dfa = RookDFA()
        self.board = Board()

        # Set up a basic board with a rook for testing
        self.white_rook = Piece('rook', 'white', 'e1')
        self.black_rook = Piece('rook', 'black', 'e8')
        self.board.place_piece(self.white_rook, 'e1')
        self.board.place_piece(self.black_rook, 'e8')

    def test_rook_dfa_initialization(self):
        """Test that the rook DFA initializes correctly."""
        self.assertIsInstance(self.rook_dfa, RookDFA)

    def test_legal_horizontal_moves(self):
        """Test legal horizontal rook moves."""
        # Test moves along the first rank
        test_cases = [
            ('e1', 'a1', True),  # Left to edge
            ('e1', 'b1', True),  # Left one
            ('e1', 'c1', True),  # Left two
            ('e1', 'd1', True),  # Left three
            ('e1', 'f1', True),  # Right one
            ('e1', 'g1', True),  # Right two
            ('e1', 'h1', True),  # Right to edge
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.rook_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Rook move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_legal_vertical_moves(self):
        """Test legal vertical rook moves."""
        # Test moves along the e-file
        test_cases = [
            ('e1', 'e2', True),  # Up one
            ('e1', 'e3', True),  # Up two
            ('e1', 'e4', True),  # Up three
            ('e1', 'e5', True),  # Up four
            ('e1', 'e6', True),  # Up five
            ('e1', 'e7', True),  # Up six
            ('e1', 'e8', True),  # Up to edge (capture black rook)
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.rook_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Rook move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_illegal_diagonal_moves(self):
        """Test that diagonal moves are rejected."""
        test_cases = [
            ('e1', 'f2'),  # Diagonal
            ('e1', 'g3'),  # Diagonal
            ('e1', 'h4'),  # Diagonal
            ('e1', 'd2'),  # Diagonal
            ('e1', 'c3'),  # Diagonal
            ('e1', 'b4'),  # Diagonal
        ]

        for from_sq, to_sq in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.rook_dfa.validate(self.board, from_sq, to_sq)
                self.assertFalse(result['valid'],
                               f"Rook move {from_sq}->{to_sq} should be illegal (diagonal)")
                self.assertIn("horizontally or vertically", result['reason'])

    def test_blocked_path(self):
        """Test that blocked paths are correctly detected."""
        # Place a blocking piece
        blocking_piece = Piece('pawn', 'white', 'e3')
        self.board.place_piece(blocking_piece, 'e3')

        # Test moves that should be blocked
        test_cases = [
            ('e1', 'e4'),  # Blocked by pawn at e3
            ('e1', 'e5'),  # Blocked by pawn at e3
            ('e1', 'e6'),  # Blocked by pawn at e3
            ('e1', 'e7'),  # Blocked by pawn at e3
            ('e1', 'e8'),  # Blocked by pawn at e3
        ]

        for from_sq, to_sq in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.rook_dfa.validate(self.board, from_sq, to_sq)
                self.assertFalse(result['valid'],
                               f"Rook move {from_sq}->{to_sq} should be illegal (blocked)")
                self.assertIn("blocked", result['reason'].lower())

    def test_capture_moves(self):
        """Test that capturing enemy pieces works."""
        # Test capturing the black rook
        result = self.rook_dfa.validate(self.board, 'e1', 'e8')
        self.assertTrue(result['valid'],
                       "Rook should be able to capture enemy piece")
        self.assertIn("Legal rook move", result['reason'])

    def test_cannot_capture_friendly(self):
        """Test that capturing friendly pieces is not allowed."""
        # Place a friendly piece in the way
        friendly_piece = Piece('pawn', 'white', 'e3')
        self.board.place_piece(friendly_piece, 'e3')

        # Try to move past the friendly piece (should be blocked)
        result = self.rook_dfa.validate(self.board, 'e1', 'e4')
        self.assertFalse(result['valid'],
                       "Rook should not be able to move past friendly piece")

        # Try to move onto the friendly piece (should be rejected)
        result = self.rook_dfa.validate(self.board, 'e1', 'e3')
        self.assertFalse(result['valid'],
                       "Rook should not be able to capture friendly piece")
        self.assertIn("own piece", result['reason'])

    def test_same_square_rejected(self):
        """Test that moving to the same square is rejected."""
        result = self.rook_dfa.validate(self.board, 'e1', 'e1')
        self.assertFalse(result['valid'])
        self.assertIn("same square", result['reason'].lower())

    def test_no_piece_at_start(self):
        """Test that moves are rejected when there's no rook at start."""
        # Clear the e1 square
        self.board.remove_piece('e1')

        result = self.rook_dfa.validate(self.board, 'e1', 'e4')
        self.assertFalse(result['valid'])
        self.assertIn("No rook", result['reason'])

    def test_wrong_piece_type(self):
        """Test that moves are rejected when the wrong piece type is at start."""
        # Put a pawn at e1 instead of a rook
        self.board.remove_piece('e1')
        pawn = Piece('pawn', 'white', 'e1')
        self.board.place_piece(pawn, 'e1')

        result = self.rook_dfa.validate(self.board, 'e1', 'e4')
        self.assertFalse(result['valid'])
        self.assertIn("No rook", result['reason'])


if __name__ == '__main__':
    unittest.main()