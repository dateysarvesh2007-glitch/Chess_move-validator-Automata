"""
Tests for castling validation.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.layer2.castling import CastlingValidator
from src.game_state import GameState
from src.board import Board
from src.piece import Piece


class TestCastling(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.game_state = GameState()
        self.castling_validator = CastlingValidator(self.game_state)

    def test_initial_castling_rights(self):
        """Test that castling is initially possible for both sides."""
        # White castling
        result = self.castling_validator.validate_castling('white', True)   # Kingside
        self.assertTrue(result['valid'],
                       f"White kingside castling should be initially possible: {result['reason']}")

        result = self.castling_validator.validate_castling('white', False)  # Queenside
        self.assertTrue(result['valid'],
                       f"White queenside castling should be initially possible: {result['reason']}")

        # Black castling
        result = self.castling_validator.validate_castling('black', True)   # Kingside
        self.assertTrue(result['valid'],
                       f"Black kingside castling should be initially possible: {result['reason']}")

        result = self.castling_validator.validate_castling('black', False)  # Queenside
        self.assertTrue(result['valid'],
                       f"Black queenside castling should be initially possible: {result['reason']}")

    def test_losing_castling_rights_after_king_move(self):
        """Test that castling rights are lost after king moves."""
        # Move the white king
        self.game_state.board.remove_piece('e1')
        white_king = Piece('king', 'white', 'e2')
        self.game_state.board.place_piece(white_king, 'e2')
        self.game_state.castling_rights['white']['kingside'] = False
        self.game_state.castling_rights['white']['queenside'] = False

        # White should lose both castling rights
        result = self.castling_validator.validate_castling('white', True)   # Kingside
        self.assertFalse(result['valid'],
                        "White should lose kingside castling rights after king moves")
        self.assertIn("king has moved", result['reason'])

        result = self.castling_validator.validate_castling('white', False)  # Queenside
        self.assertFalse(result['valid'],
                        "White should lose queenside castling rights after king moves")
        self.assertIn("king has moved", result['reason'])

    def test_losing_castling_rights_after_rook_move(self):
        """Test that castling rights are lost after rook moves."""
        # Move the white kingside rook
        self.game_state.board.remove_piece('h1')
        white_rook = Piece('rook', 'white', 'h2')
        self.game_state.board.place_piece(white_rook, 'h2')
        self.game_state.castling_rights['white']['kingside'] = False

        # White should lose kingside castling rights
        result = self.castling_validator.validate_castling('white', True)   # Kingside
        self.assertFalse(result['valid'],
                        "White should lose kingside castling rights after rook moves")
        self.assertIn("rook has moved", result['reason'])

        # Queenside should still be possible
        result = self.castling_validator.validate_castling('white', False)  # Queenside
        self.assertTrue(result['valid'],
                       f"White queenside castling should still be possible: {result['reason']}")

    def test_castling_path_blocking(self):
        """Test that castling is blocked when pieces are in the way."""
        # Place a piece blocking white kingside castling path
        blocker = Piece('pawn', 'white', 'f1')
        self.game_state.board.place_piece(blocker, 'f1')

        # White kingside castling should be blocked
        result = self.castling_validator.validate_castling('white', True)   # Kingside
        self.assertFalse(result['valid'],
                        "White kingside castling should be blocked by f1 pawn")
        self.assertIn("blocking", result['reason'].lower())

        # Place a piece blocking white queenside castling path
        self.game_state.board.remove_piece('f1')  # Remove first blocker
        blocker2 = Piece('pawn', 'white', 'd1')
        self.game_state.board.place_piece(blocker2, 'd1')

        # White queenside castling should be blocked
        result = self.castling_validator.validate_castling('white', False)  # Queenside
        self.assertFalse(result['valid'],
                        "White queenside castling should be blocked by d1 pawn")
        self.assertIn("blocking", result['reason'].lower())

    def test_get_castling_move(self):
        """Test getting the actual castling moves."""
        # Test white kingside castling
        castling_move = self.castling_validator.get_castling_move('white', True)
        self.assertIsNotNone(castling_move)
        king_from, king_to, rook_from, rook_to = castling_move
        self.assertEqual(king_from, 'e1')
        self.assertEqual(king_to, 'g1')
        self.assertEqual(rook_from, 'h1')
        self.assertEqual(rook_to, 'f1')

        # Test white queenside castling
        castling_move = self.castling_validator.get_castling_move('white', False)
        self.assertIsNotNone(castling_move)
        king_from, king_to, rook_from, rook_to = castling_move
        self.assertEqual(king_from, 'e1')
        self.assertEqual(king_to, 'c1')
        self.assertEqual(rook_from, 'a1')
        self.assertEqual(rook_to, 'd1')

        # Test black kingside castling
        castling_move = self.castling_validator.get_castling_move('black', True)
        self.assertIsNotNone(castling_move)
        king_from, king_to, rook_from, rook_to = castling_move
        self.assertEqual(king_from, 'e8')
        self.assertEqual(king_to, 'g8')
        self.assertEqual(rook_from, 'h8')
        self.assertEqual(rook_to, 'f8')

        # Test black queenside castling
        castling_move = self.castling_validator.get_castling_move('black', False)
        self.assertIsNotNone(castling_move)
        king_from, king_to, rook_from, rook_to = castling_move
        self.assertEqual(king_from, 'e8')
        self.assertEqual(king_to, 'c8')
        self.assertEqual(rook_from, 'a8')
        self.assertEqual(rook_to, 'd8')


if __name__ == '__main__':
    unittest.main()