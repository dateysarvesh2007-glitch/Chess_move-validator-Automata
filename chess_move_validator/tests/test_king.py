"""
Tests for the King DFA movement validator.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.layer1.king import KingDFA
from src.board import Board
from src.piece import Piece


class TestKingDFA(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.king_dfa = KingDFA()
        self.board = Board()

        # Set up a basic board with a king for testing
        self.white_king = Piece('king', 'white', 'e1')
        self.black_king = Piece('king', 'black', 'e8')
        self.board.place_piece(self.white_king, 'e1')
        self.board.place_piece(self.black_king, 'e8')

    def test_king_dfa_initialization(self):
        """Test that the king DFA initializes correctly."""
        self.assertIsInstance(self.king_dfa, KingDFA)

    def test_legal_king_moves(self):
        """Test legal king moves (one square in any direction)."""
        # From e1, king can move to:
        # d1, e2, f1 (left, up, right)
        # d2, f2 (diagonals)
        test_cases = [
            ('e1', 'd1', True),  # Left
            ('e1', 'e2', True),  # Up
            ('e1', 'f1', True),  # Right
            ('e1', 'd2', True),  # Diagonal up-left
            ('e1', 'f2', True),  # Diagonal up-right
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.king_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"King move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_illegal_king_moves(self):
        """Test illegal king moves (more than one square)."""
        test_cases = [
            ('e1', 'e3'),    # Two squares up
            ('e1', 'e4'),    # Three squares up
            ('e1', 'c1'),    # Two squares left
            ('e1', 'a1'),    # Four squares left
            ('e1', 'g1'),    # Two squares right
            ('e1', 'h1'),    # Three squares right
            ('e1', 'c3'),    # Two squares up, two left (too far)
            ('e1', 'g3'),    # Two squares up, two right (too far)
        ]

        for from_sq, to_sq in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.king_dfa.validate(self.board, from_sq, to_sq)
                self.assertFalse(result['valid'],
                               f"King move {from_sq}->{to_sq} should be illegal (more than one square)")
                self.assertIn("one square", result['reason'])

    def test_capture_moves(self):
        """Test that capturing enemy pieces works."""
        # Place an enemy piece where the king can capture it
        self.board.remove_piece('e8')  # Remove black king from e8
        enemy_queen = Piece('queen', 'black', 'f2')  # King can capture diagonally
        self.board.place_piece(enemy_queen, 'f2')

        result = self.king_dfa.validate(self.board, 'e1', 'f2')
        self.assertTrue(result['valid'],
                       "King should be able to capture enemy piece")
        self.assertIn("Legal king move", result['reason'])

    def test_cannot_capture_friendly(self):
        """Test that capturing friendly pieces is not allowed."""
        # Place a friendly piece where the king would move
        friendly_piece = Piece('pawn', 'white', 'f2')
        self.board.place_piece(friendly_piece, 'f2')

        # Try to move onto the friendly piece (should be rejected)
        result = self.king_dfa.validate(self.board, 'e1', 'f2')
        self.assertFalse(result['valid'],
                       "King should not be able to capture friendly piece")
        self.assertIn("own piece", result['reason'])

    def test_same_square_rejected(self):
        """Test that moving to the same square is rejected."""
        result = self.king_dfa.validate(self.board, 'e1', 'e1')
        self.assertFalse(result['valid'])
        self.assertIn("same square", result['reason'].lower())

    def test_no_piece_at_start(self):
        """Test that moves are rejected when there's no king at start."""
        # Clear the e1 square
        self.board.remove_piece('e1')

        result = self.king_dfa.validate(self.board, 'e1', 'e2')
        self.assertFalse(result['valid'])
        self.assertIn("No king", result['reason'])

    def test_wrong_piece_type(self):
        """Test that moves are rejected when the wrong piece type is at start."""
        # Put a pawn at e1 instead of a king
        self.board.remove_piece('e1')
        pawn = Piece('pawn', 'white', 'e1')
        self.board.place_piece(pawn, 'e1')

        result = self.king_dfa.validate(self.board, 'e1', 'e2')
        self.assertFalse(result['valid'])
        self.assertIn("No king", result['reason'])


if __name__ == '__main__':
    unittest.main()