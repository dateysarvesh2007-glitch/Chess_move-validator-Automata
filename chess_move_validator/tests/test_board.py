"""
Tests for the chess board representation.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.board import Board
from src.piece import Piece


class TestBoard(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.board = Board()

    def test_board_initialization(self):
        """Test that the board initializes as empty."""
        # All squares should be empty
        for row in range(8):
            for col in range(8):
                self.assertIsNone(self.board.get_piece_at(row, col),
                                f"Square at ({row}, {col}) should be empty")

    def test_place_and_get_piece(self):
        """Test placing and retrieving pieces."""
        # Create a test piece
        piece = Piece('king', 'white', 'e1')

        # Place the piece
        self.board.place_piece(piece, 'e1')

        # Retrieve the piece
        retrieved_piece = self.board.get_piece('e1')
        self.assertEqual(retrieved_piece, piece)
        self.assertEqual(retrieved_piece.piece_type, 'king')
        self.assertEqual(retrieved_piece.color, 'white')
        self.assertEqual(retrieved_piece.position, 'e1')

    def test_remove_piece(self):
        """Test removing pieces from the board."""
        # Place a piece
        piece = Piece('queen', 'black', 'd4')
        self.board.place_piece(piece, 'd4')

        # Verify it's there
        self.assertIsNotNone(self.board.get_piece('d4'))

        # Remove it
        self.board.remove_piece('d4')

        # Verify it's gone
        self.assertIsNone(self.board.get_piece('d4'))

    def test_is_empty(self):
        """Test checking if squares are empty."""
        # New board should be empty everywhere
        self.assertTrue(self.board.is_empty('a1'))
        self.assertTrue(self.board.is_empty('h8'))
        self.assertTrue(self.board.is_empty('e4'))

        # Place a piece and check
        piece = Piece('rook', 'white', 'a1')
        self.board.place_piece(piece, 'a1')
        self.assertFalse(self.board.is_empty('a1'))
        self.assertTrue(self.board.is_empty('a2'))  # Should still be empty

    def test_is_occupied_by(self):
        """Test checking if squares are occupied by specific colors."""
        # Place a white piece
        white_piece = Piece('knight', 'white', 'g1')
        self.board.place_piece(white_piece, 'g1')

        # Place a black piece
        black_piece = Piece('knight', 'black', 'g8')
        self.board.place_piece(black_piece, 'g8')

        # Check white occupation
        self.assertTrue(self.board.is_occupied_by('g1', 'white'))
        self.assertFalse(self.board.is_occupied_by('g1', 'black'))

        # Check black occupation
        self.assertTrue(self.board.is_occupied_by('g8', 'black'))
        self.assertFalse(self.board.is_occupied_by('g8', 'white'))

        # Check empty square
        self.assertFalse(self.board.is_occupied_by('e4', 'white'))
        self.assertFalse(self.board.is_occupied_by('e4', 'black'))

    def test_board_copy(self):
        """Test creating a copy of the board."""
        # Place some pieces
        pieces = [
            Piece('king', 'white', 'e1'),
            Piece('queen', 'black', 'd8'),
            Piece('pawn', 'white', 'e2'),
            Piece('rook', 'black', 'a8')
        ]

        for piece in pieces:
            self.board.place_piece(piece, piece.position)

        # Create a copy
        copied_board = self.board.copy()

        # Verify pieces are in the same positions
        for piece in pieces:
            original_piece = self.board.get_piece(piece.position)
            copied_piece = copied_board.get_piece(piece.position)

            self.assertIsNotNone(copied_piece)
            self.assertEqual(original_piece.piece_type, copied_piece.piece_type)
            self.assertEqual(original_piece.color, copied_piece.color)
            self.assertEqual(original_piece.position, copied_piece.position)

        # Verify they are different objects (deep copy)
        for piece in pieces:
            original_piece = self.board.get_piece(piece.position)
            copied_piece = copied_board.get_piece(piece.position)
            self.assertIsNot(original_piece, copied_piece)

    def test_board_display(self):
        """Test that the board can display itself."""
        # This should not raise an exception
        display_string = self.board.display()
        self.assertIsInstance(display_string, str)
        self.assertGreater(len(display_string), 0)

        # Test with some pieces
        piece = Piece('king', 'white', 'e1')
        self.board.place_piece(piece, 'e1')
        display_string = self.board.display()
        self.assertIn('♔', display_string)  # White king symbol


if __name__ == '__main__':
    unittest.main()