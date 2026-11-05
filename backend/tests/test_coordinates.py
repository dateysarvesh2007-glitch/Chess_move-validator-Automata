"""
Tests for coordinate conversion utilities.
"""

import unittest
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from coordinates import square_to_coordinates, coordinates_to_square, is_valid_square


class TestCoordinates(unittest.TestCase):

    def test_square_to_coordinates(self):
        """Test converting algebraic notation to coordinates."""
        # Test normal squares
        self.assertEqual(square_to_coordinates("a1"), (0, 0))
        self.assertEqual(square_to_coordinates("h1"), (0, 7))
        self.assertEqual(square_to_coordinates("a8"), (7, 0))
        self.assertEqual(square_to_coordinates("h8"), (7, 7))
        self.assertEqual(square_to_coordinates("e4"), (3, 4))
        self.assertEqual(square_to_coordinates("d5"), (4, 3))

        # Test edge cases
        self.assertEqual(square_to_coordinates("a1"), (0, 0))  # Bottom-left
        self.assertEqual(square_to_coordinates("h8"), (7, 7))  # Top-right

    def test_coordinates_to_square(self):
        """Test converting coordinates to algebraic notation."""
        # Test normal squares
        self.assertEqual(coordinates_to_square(0, 0), "a1")
        self.assertEqual(coordinates_to_square(0, 7), "h1")
        self.assertEqual(coordinates_to_square(7, 0), "a8")
        self.assertEqual(coordinates_to_square(7, 7), "h8")
        self.assertEqual(coordinates_to_square(3, 4), "e4")
        self.assertEqual(coordinates_to_square(4, 3), "d5")

        # Test edge cases
        self.assertEqual(coordinates_to_square(0, 0), "a1")  # Bottom-left
        self.assertEqual(coordinates_to_square(7, 7), "h8")  # Top-right

    def test_round_trip(self):
        """Test that converting back and forth gives the original value."""
        test_squares = ["a1", "h1", "a8", "h8", "e4", "d5", "c3", "f6"]
        for square in test_squares:
            coords = square_to_coordinates(square)
            back_to_square = coordinates_to_square(coords[0], coords[1])
            self.assertEqual(square, back_to_square,
                           f"Round trip failed for {square}: {square} -> {coords} -> {back_to_square}")

    def test_is_valid_square(self):
        """Test square validation."""
        # Valid squares
        self.assertTrue(is_valid_square("a1"))
        self.assertTrue(is_valid_square("h8"))
        self.assertTrue(is_valid_square("e4"))
        self.assertTrue(is_valid_square("d5"))

        # Invalid squares
        self.assertFalse(is_valid_square("i1"))   # Invalid file
        self.assertFalse(is_valid_square("a9"))   # Invalid rank
        self.assertFalse(is_valid_square("z0"))   # Invalid file and rank
        self.assertFalse(is_valid_square("a"))    # Too short
        self.assertFalse(is_valid_square("abcd")) # Too long
        self.assertFalse(is_valid_square(""))     # Empty string
        self.assertFalse(is_valid_square("a1b"))  # Too long

    def test_coordinate_bounds(self):
        """Test that coordinates are properly bounded."""
        # Valid coordinates should work
        self.assertEqual(square_to_coordinates("a1"), (0, 0))
        self.assertEqual(square_to_coordinates("h8"), (7, 7))

        # Invalid coordinates should raise ValueError
        with self.assertRaises(ValueError):
            square_to_coordinates("i1")  # File too high

        with self.assertRaises(ValueError):
            square_to_coordinates("a9")  # Rank too high

        with self.assertRaises(ValueError):
            square_to_coordinates("a0")  # Rank too low

        with self.assertRaises(ValueError):
            square_to_coordinates("z1")  # Invalid file


if __name__ == '__main__':
    unittest.main()