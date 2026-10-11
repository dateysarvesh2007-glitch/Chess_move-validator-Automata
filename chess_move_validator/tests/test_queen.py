"""
Tests for the Queen DFA movement validator.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.layer1.queen import QueenDFA
from src.board import Board
from src.piece import Piece


class TestQueenDFA(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.queen_dfa = QueenDFA()
        self.board = Board()

        # Set up a basic board with a queen for testing
        self.white_queen = Piece('queen', 'white', 'd1')
        self.black_queen = Piece('queen', 'black', 'd8')
        self.board.place_piece(self.white_queen, 'd1')
        self.board.place_piece(self.black_queen, 'd8')

    def test_queen_dfa_initialization(self):
        """Test that the queen DFA initializes correctly."""
        self.assertIsInstance(self.queen_dfa, QueenDFA)

    def test_queen_moves_like_rook(self):
        """Test that queen can move like a rook (horizontally/vertically)."""
        # Test horizontal moves (like rook)
        horizontal_cases = [
            ('d1', 'a1', True),  # Left to edge
            ('d1', 'b1', True),  # Left
            ('d1', 'c1', True),  # Left
            ('d1', 'e1', True),  # Right
            ('d1', 'f1', True),  # Right
            ('d1', 'g1', True),  # Right
            ('d1', 'h1', True),  # Right to edge
        ]

        for from_sq, to_sq, expected in horizontal_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq, direction='horizontal'):
                result = self.queen_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Queen move {from_sq}->{to_sq} (rook-like) should be {'legal' if expected else 'illegal'}")

        # Test vertical moves (like rook)
        vertical_cases = [
            ('d1', 'd2', True),  # Up
            ('d1', 'd3', True),  # Up
            ('d1', 'd4', True),  # Up
            ('d1', 'd5', True),  # Up
            ('d1', 'd6', True),  # Up
            ('d1', 'd7', True),  # Up
            ('d1', 'd8', True),  # Up to edge (capture black queen)
        ]

        for from_sq, to_sq, expected in vertical_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq, direction='vertical'):
                result = self.queen_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Queen move {from_sq}->{to_sq} (rook-like) should be {'legal' if expected else 'illegal'}")

    def test_queen_moves_like_bishop(self):
        """Test that queen can move like a bishop (diagonally)."""
        # Test diagonal moves (like bishop)
        diagonal_cases = [
            ('d1', 'a4', True),  # Diagonal up-left
            ('d1', 'b3', True),  # Diagonal up-left
            ('d1', 'c2', True),  # Diagonal up-left
            ('d1', 'e2', True),  # Diagonal up-right
            ('d1', 'f3', True),  # Diagonal up-right
            ('d1', 'g4', True),  # Diagonal up-right
            ('d1', 'h5', True),  # Diagonal up-right to edge
        ]

        for from_sq, to_sq, expected in diagonal_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq, direction='diagonal'):
                result = self.queen_dfa.validate(self.board, from_sq, to_sq)
                self.assertEqual(result['valid'], expected,
                               f"Queen move {from_sq}->{to_sq} (bishop-like) should be {'legal' if expected else 'illegal'}")

    def test_illegal_queen_moves(self):
        """Test illegal queen moves (not horizontal, vertical, or diagonal)."""
        test_cases = [
            ('d1', 'b2'),    # Knight move
            ('d1', 'a3'),    # Not straight or diagonal (2 left, 2 up)
            ('d1', 'f5'),    # Not straight or diagonal (2 right, 4 up)
        ]

        for from_sq, to_sq in test_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.queen_dfa.validate(self.board, from_sq, to_sq)
                self.assertFalse(result['valid'],
                               f"Queen move {from_sq}->{to_sq} should be illegal (not straight/diagonal)")
                self.assertIn("horizontally, vertically, or diagonally", result['reason'])

    def test_blocked_path(self):
        """Test that blocked paths are correctly detected."""
        # Place a blocking piece
        blocking_piece = Piece('pawn', 'white', 'd3')
        self.board.place_piece(blocking_piece, 'd3')

        # Test moves that should be blocked (vertical)
        blocked_cases = [
            ('d1', 'd4'),  # Blocked by pawn at d3
            ('d1', 'd5'),  # Blocked by pawn at d3
            ('d1', 'd6'),  # Blocked by pawn at d3
            ('d1', 'd7'),  # Blocked by pawn at d3
            ('d1', 'd8'),  # Blocked by pawn at d3
        ]

        for from_sq, to_sq in blocked_cases:
            with self.subTest(from_square=from_sq, to_square=to_sq):
                result = self.queen_dfa.validate(self.board, from_sq, to_sq)
                self.assertFalse(result['valid'],
                               f"Queen move {from_sq}->{to_sq} should be illegal (blocked)")
                self.assertIn("blocked", result['reason'].lower())

        # Test moves that should be blocked (diagonal)
        # Place blocker on diagonal
        self.board.remove_piece('d3')
        blocker_diag = Piece('pawn', 'white', 'b3')
        self.board.place_piece(blocker_diag, 'b3')

        diagonal_blocked_cases = [
            ('d1', 'a4'),  # Blocked by pawn at b3
            ('d1', 'c2'),  # Actually, this is before the blocker - should be legal
            ('d1', 'e2'),  # Different diagonal - should be legal
            ('d1', 'f3'),  # Different diagonal - should be legal
            ('d1', 'g4'),  # Different diagonal - should be legal
            ('d1', 'h5'),  # Different diagonal - should be legal
        ]

        # d1 to c2 should be legal (before blocker at b3)
        result = self.queen_dfa.validate(self.board, 'd1', 'c2')
        self.assertTrue(result['valid'],
                       "Queen move d1->c2 should be legal (before blocker)")

        # d1 to a4 should be blocked by pawn at b3
        result = self.queen_dfa.validate(self.board, 'd1', 'a4')
        self.assertFalse(result['valid'],
                       "Queen move d1->a4 should be illegal (blocked by b3)")
        self.assertIn("blocked", result['reason'].lower())

    def test_capture_moves(self):
        """Test that capturing enemy pieces works."""
        # Test capturing like a rook (vertical)
        self.board.remove_piece('d8')
        target_rook = Piece('rook', 'black', 'd8')
        self.board.place_piece(target_rook, 'd8')

        result = self.queen_dfa.validate(self.board, 'd1', 'd8')
        self.assertTrue(result['valid'],
                       "Queen should be able to capture enemy piece (rook-like)")
        self.assertIn("Linear vertical advance", result['reason'])

        # Test capturing like a bishop (diagonal)
        self.board.remove_piece('d8')
        target_bishop = Piece('bishop', 'black', 'a4')
        self.board.place_piece(target_bishop, 'a4')

        result = self.queen_dfa.validate(self.board, 'd1', 'a4')
        self.assertTrue(result['valid'],
                       "Queen should be able to capture enemy piece (bishop-like)")
        self.assertIn("Diagonal advance", result['reason'])

    def test_cannot_capture_friendly(self):
        """Test that capturing friendly pieces is not allowed."""
        # Place a friendly piece in the way vertically
        friendly_piece = Piece('pawn', 'white', 'd3')
        self.board.place_piece(friendly_piece, 'd3')

        # Try to move past the friendly piece (should be blocked)
        result = self.queen_dfa.validate(self.board, 'd1', 'd4')
        self.assertFalse(result['valid'],
                       "Queen should not be able to move past friendly piece")

        # Try to move onto the friendly piece (should be rejected)
        result = self.queen_dfa.validate(self.board, 'd1', 'd3')
        self.assertFalse(result['valid'],
                       "Queen should not be able to capture friendly piece")
        self.assertIn("own piece", result['reason'])

    def test_same_square_rejected(self):
        """Test that moving to the same square is rejected."""
        result = self.queen_dfa.validate(self.board, 'd1', 'd1')
        self.assertFalse(result['valid'])
        self.assertIn("same square", result['reason'].lower())

    def test_no_piece_at_start(self):
        """Test that moves are rejected when there's no queen at start."""
        # Clear the d1 square
        self.board.remove_piece('d1')

        result = self.queen_dfa.validate(self.board, 'd1', 'e1')
        self.assertFalse(result['valid'])
        self.assertIn("No queen", result['reason'])

    def test_wrong_piece_type(self):
        """Test that moves are rejected when the wrong piece type is at start."""
        # Put a pawn at d1 instead of a queen
        self.board.remove_piece('d1')
        pawn = Piece('pawn', 'white', 'd1')
        self.board.place_piece(pawn, 'd1')

        result = self.queen_dfa.validate(self.board, 'd1', 'e1')
        self.assertFalse(result['valid'])
        self.assertIn("No queen", result['reason'])


if __name__ == '__main__':
    unittest.main()