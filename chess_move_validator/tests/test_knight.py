"""
Tests for the Knight DFA movement validator.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from layer1.knight import KnightDFA
from board import Board
from piece import Piece


class TestKnightDFA(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.knight_dfa = KnightDFA()
        self.board = Board()

        # Set up a basic board with a knight for testing
        self.white_knight = Piece('knight', 'white', 'e1')
        self.black_knight = Piece('knight', 'black', 'e8')
        self.board.place_piece(self.white_knight, 'e1')
        self.board.place_piece(self.black_knight, 'e8')

    def test_knight_dfa_initialization(self):
        """Test that the knight DFA initializes correctly."""
        self.assertIsInstance(self.knight_dfa, KnightDFA)

    def test_legal_knight_moves(self):
        """Test legal knight moves (L-shape: 2+1 or 1+2)."""
        # From e1, knights can go to:
        # c2, d3, f3, g2 (2 up, 1 left/right or 1 up, 2 left/right)
        # But since e1 is on rank 1, only moves going up are possible:
        # Actually, from e1 (file 5, rank 1):
        # - 2 up, 1 left: c2 (file 3, rank 2)
        # - 2 up, 1 right: g2 (file 7, rank 2)
        # - 1 up, 2 left: d3 (file 4, rank 3)
        # - 1 up, 2 right: f3 (file 6, rank 3)

        test_cases = [
            ('e1', 'c2', True),  # 2 up, 1 left
            ('e1', 'd3', True),  # 1 up, 2 left
            ('e1', 'f3', True),  # 1 up, 2 right
            ('e1', 'g2', True),  # 2 up, 1 right
        ]

        for from_sq, to_sq, expected in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.knight_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Knight move {from_sq}->{to_sq} should be {'legal' if expected else 'illegal'}")

    def test_illegal_knight_moves(self):
        """Test illegal knight moves (non-L-shape)."""
        test_cases = [
            ('e1', 'e2'),   # 1 up (not L-shape)
            ('e1', 'e3'),   # 2 up (not L-shape)
            ('e1', 'd1'),   # 1 left (not L-shape)
            ('e1', 'f1'),   # 1 right (not L-shape)
            ('e1', 'c1'),   # 2 left (not L-shape)
            ('e1', 'h1'),   # 3 right (not L-shape)
            ('e1', 'd2'),   # 1 up, 1 left (diagonal, not L-shape)
            ('e1', 'e4'),   # 3 up (not L-shape)
            ('e1', 'a1'),   # 4 left (not L-shape)
            ('e1', 'h5'),   # Too far
        ]

        for from_sq, to_sq in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.knight_dfa.validate(self.board, from_sq, to_sq)
                self.assertFalse(result['valid'],
                               f"Knight move {from_sq}->{to_sq} should be illegal (not L-shape)")
                # Same square is handled separately
                if from_sq != to_sq:
                    self.assertIn("L-shape", result['reason'])

    def test_same_square_rejected(self):
        """Test that moving to the same square is rejected."""
        result = self.knight_dfa.validate(self.board, 'e1', 'e1')
        self.assertFalse(result['valid'])
        self.assertIn("same square", result['reason'].lower())

    def test_capture_moves(self):
        """Test that capturing enemy pieces works."""
        # Place a black knight where white knight can capture it
        self.board.remove_piece('e8')  # Remove black knight from e8
        target_knight = Piece('knight', 'black', 'f3')  # White knight can go to f3
        self.board.place_piece(target_knight, 'f3')

        result = self.knight_dfa.validate(self.board, 'e1', 'f3')
        self.assertTrue(result['valid'],
                       "Knight should be able to capture enemy piece")
        self.assertIn("Legal knight move", result['reason'])

    def test_cannot_capture_friendly(self):
        """Test that capturing friendly pieces is not allowed."""
        # Place a friendly piece where the knight would move
        friendly_piece = Piece('pawn', 'white', 'f3')
        self.board.place_piece(friendly_piece, 'f3')

        # Try to move onto the friendly piece (should be rejected)
        result = self.knight_dfa.validate(self.board, 'e1', 'f3')
        self.assertFalse(result['valid'],
                       "Knight should not be able to capture friendly piece")
        self.assertIn("own piece", result['reason'])

    def test_knights_can_jump(self):
        """Test that knights can jump over pieces."""
        # Place pieces in potential path
        blocking_piece1 = Piece('pawn', 'white', 'd2')  # Not actually blocking for knight
        blocking_piece2 = Piece('pawn', 'white', 'e2')  # Not actually blocking for knight
        self.board.place_piece(blocking_piece1, 'd2')
        self.board.place_piece(blocking_piece2, 'e2')

        # Knight move should still work because knights jump
        result = self.knight_dfa.validate(self.board, 'e1', 'f3')
        self.assertTrue(result['valid'],
                       "Knight should be able to jump over pieces")
        self.assertIn("Legal knight move", result['reason'])

    def test_no_piece_at_start(self):
        """Test that moves are rejected when there's no knight at start."""
        # Clear the e1 square
        self.board.remove_piece('e1')

        result = self.knight_dfa.validate(self.board, 'e1', 'f3')
        self.assertFalse(result['valid'])
        self.assertIn("No knight", result['reason'])

    def test_wrong_piece_type(self):
        """Test that moves are rejected when the wrong piece type is at start."""
        # Put a pawn at e1 instead of a knight
        self.board.remove_piece('e1')
        pawn = Piece('pawn', 'white', 'e1')
        self.board.place_piece(pawn, 'e1')

        result = self.knight_dfa.validate(self.board, 'e1', 'f3')
        self.assertFalse(result['valid'])
        self.assertIn("No knight", result['reason'])


if __name__ == '__main__':
    unittest.main()