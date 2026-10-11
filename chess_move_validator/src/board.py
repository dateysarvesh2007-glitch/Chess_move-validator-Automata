"""
Chess board representation and management.
Represents the 8x8 chess board and provides methods for piece placement and retrieval.
"""

from piece import Piece
from coordinates import square_to_coordinates, coordinates_to_square


class Board:
    """
    Represents a chess board as an 8x8 grid.

    The board is stored as a 2D list where:
    - board[row][col] contains either None (empty square) or a Piece object
    - row 0 corresponds to rank 1 (a1-h1)
    - row 7 corresponds to rank 8 (a8-h8)
    - col 0 corresponds to file 'a'
    - col 7 corresponds to file 'h'
    """

    def __init__(self):
        """Initialize an empty 8x8 board."""
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def place_piece(self, piece, square):
        """
        Place a piece on the board at the specified square.

        Args:
            piece (Piece): The piece to place
            square (str): Chess square in algebraic notation (e.g., "e4")
        """
        row, col = square_to_coordinates(square)
        self.grid[row][col] = piece

    def get_piece(self, square):
        """
        Get the piece at the specified square.

        Args:
            square (str): Chess square in algebraic notation (e.g., "e4")

        Returns:
            Piece or None: The piece at the square, or None if empty
        """
        row, col = square_to_coordinates(square)
        return self.grid[row][col]

    def remove_piece(self, square):
        """
        Remove a piece from the board at the specified square.

        Args:
            square (str): Chess square in algebraic notation (e.g., "e4")
        """
        row, col = square_to_coordinates(square)
        self.grid[row][col] = None

    def is_empty(self, square):
        """
        Check if a square is empty.

        Args:
            square (str): Chess square in algebraic notation (e.g., "e4")

        Returns:
            bool: True if square is empty, False otherwise
        """
        return self.get_piece(square) is None

    def is_occupied_by(self, square, color):
        """
        Check if a square is occupied by a piece of the specified color.

        Args:
            square (str): Chess square in algebraic notation (e.g., "e4")
            color (str): 'white' or 'black'

        Returns:
            bool: True if square contains a piece of the specified color, False otherwise
        """
        piece = self.get_piece(square)
        return piece is not None and piece.color == color

    def get_piece_at(self, row, col):
        """
        Get piece at specific row, column indices (internal use).

        Args:
            row (int): Row index (0-7)
            col (int): Column index (0-7)

        Returns:
            Piece or None: The piece at the position, or None if empty
        """
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None

    def copy(self):
        """
        Create a deep copy of the board.

        Returns:
            Board: A new Board instance with the same piece positions
        """
        new_board = Board()
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece is not None:
                    # Create a new piece with the same properties
                    new_piece = Piece(piece.piece_type, piece.color,
                                    coordinates_to_square(row, col))
                    new_board.grid[row][col] = new_piece
        return new_board

    def display(self):
        """
        Display the board in a human-readable format.

        Returns:
            str: String representation of the board
        """
        lines = []
        lines.append("  a b c d e f g h")
        lines.append("  ---------------")

        for row in range(7, -1, -1):  # Start from rank 8 (row 7) down to rank 1 (row 0)
            row_display = f"{row+1} "
            for col in range(8):
                piece = self.grid[row][col]
                if piece is None:
                    row_display += ". "
                else:
                    # Use ASCII symbols for better console compatibility
                    symbol = piece.get_symbol(use_unicode=False)
                    row_display += f"{symbol} "
            row_display += f"{row+1}"
            lines.append(row_display)

        lines.append("  ---------------")
        lines.append("  a b c d e f g h")
        return "\n".join(lines)


# Automata Theory Notes for Board:
# The board represents the state against which DFAs in Layer 1 operate.
# Each DFA takes the current board state as part of its input alphabet
# when validating transitions (movements).