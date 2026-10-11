"""
Tests for the Bishop DFA movement validator.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from layer1.bishop import BishopDFA
from board import Board
from piece import Piece


class TestBishopDFA(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.bishop_dfa = BishopDFA()
        self.board = Board()

        # Set up a basic board with a bishop for testing
        self.white_bishop = Piece('bishop', 'white', 'e1')
        self.black_bishop = Piece('bishop', 'black', 'e8')
        self.board.place_piece(self.white_bishop, 'e1')
        self.board.place_piece(self.black_bishop, 'e8')

    def test_bishop_dfa_initialization(self):
        """Test that the bishop DFA initializes correctly."""
        self.assertIsInstance(self.bishop_dfa, BishopDFA)

    def test_legal_diagonal_moves(self):
        """Test legal diagonal bishop moves."""
        # Test moves along the diagonal from e1
        test_cases = [
            ('e1', 'a5', True),  # Diagonal to edge
            ('e1', 'b4', True),  # Diagonal
            ('e1', 'c3', True),  # Diagonal
            ('e1', 'd2', True),  # Diagonal
            ('e1', 'f2', True),  # Diagonal
            ('e1', 'g3', True),  # Diagonal
            ('e1', 'h4', True),  # Diagonal to edge
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.bishop_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Bishop move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_illegal_straight_moves(self):
        """Test that horizontal/vertical moves are rejected."""
        test_cases = [
            ('e1', 'a1'),  # Horizontal
            ('e1', 'h1'),  # Horizontal
            ('e1', 'e2'),  # Vertical
            ('e1', 'e8'),  # Vertical
        ]

        for from_sq, to_sq in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.bishop_dfa.validate(self.board, from_sq, to_sq)
                self.assertFalse(result['valid'],
                               f"Bishop move {from_sq}->{to_sq} should be illegal (not diagonal)")
                self.assertIn("diagonally", result['reason'])

    def test_blocked_path(self):
        """Test that blocked paths are correctly detected."""
        # Place a blocking piece on the diagonal
        blocking_piece = Piece('pawn', 'white', 'c3')
        self.board.place_piece(blocking_piece, 'c3')

        # Test moves that should be blocked
        test_cases = [
            ('e1', 'd2'),  # Should be legal (before block)
            ('e1', 'b4'),  # Blocked by pawn at c3
            ('e1', 'a5'),  # Blocked by pawn at c3
            ('e1', 'f2'),  # Should be legal (other direction)
            ('e1', 'g3'),  # Should be legal (other direction)
            ('e1', 'h4'),  # Should be legal (other direction)
        ]

        for from_sq, to_sq, expected_legal in [('e1', 'd2', True), ('e1', 'b4', False),
                                              ('e1', 'a5', False), ('e1', 'f2', True),
                                              ('e1', 'g3', True), ('e1', 'h4', True)]:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.bishop_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected_legal,
                               f"Bishop move {from_sq}->{to_sq} should be {'legal' if expected_legal else 'illegal'}")
                if not expected_legal:
                    self.assertIn("blocked", result['reason'].lower())

    def test_capture_moves(self):
        """Test that capturing enemy pieces works."""
        # Test capturing the black bishop
        # Actually, e1 to e8 is not diagonal - let's correct this
        # e1 to b8 or h8 would be diagonal

        # Set up proper diagonal capture
        self.board.remove_piece('e1')  # Remove white bishop from e1
        self.board.remove_piece('e8')  # Remove black bishop from e8

        # Place white bishop at e1, black bishop at h4 (diagonal)
        self.white_bishop = Piece('bishop', 'white', 'e1')
        self.black_bishop = Piece('bishop', 'black', 'h4')
        self.board.place_piece(self.white_bishop, 'e1')
        self.board.place_piece(self.black_bishop, 'h4')

        result = self.bishop_dfa.validate(self.board, 'e1', 'h4')
        self.assertTrue(result['valid'],
                       "Bishop should be able to capture enemy piece")
        self.assertIn("Legal bishop move", result['reason'])

    def test_cannot_capture_friendly(self):
        """Test that capturing friendly pieces is not allowed."""
        # Place a friendly piece on the diagonal
        friendly_piece = Piece('pawn', 'white', 'c3')
        self.board.place_piece(friendly_piece, 'c3')

        # Try to move onto the friendly piece (should be rejected)
        result = self.bishop_dfa.validate(self.board, 'e1', 'c3')
        self.assertFalse(result['valid'],
                       "Bishop should not be able to capture friendly piece")
        self.assertIn("own piece", result['reason'])

    def test_same_square_rejected(self):
        """Test that moving to the same square is rejected."""
        result = self.bishop_dfa.validate(self.board, 'e1', 'e1')
        self.assertFalse(result['valid'])
        self.assertIn("same square", result['reason'].lower())

    def test_no_piece_at_start(self):
        """Test that moves are rejected when there's no bishop at start."""
        # Clear the e1 square
        self.board.remove_piece('e1')

        result = self.bishop_dfa.validate(self.board, 'e1', 'b2')
        self.assertFalse(result['valid'])
        self.assertIn("No bishop", result['reason'])

    def test_wrong_piece_type(self):
        """Test that moves are rejected when the wrong piece type is at start."""
        # Put a pawn at e1 instead of a bishop
        self.board.remove_piece('e1')
        pawn = Piece('pawn', 'white', 'e1')
        self.board.place_piece(pawn, 'e1')

        result = self.bishop_dfa.validate(self.board, 'e1', 'b2')
        self.assertFalse(result['valid'])
        self.assertIn("No bishop", result['reason'])


if __name__ == '__main__':
    unittest.main()