"""
Chess piece representation.
Defines the properties and basic behavior of chess pieces.
"""


class Piece:
    """
    Represents a chess piece.

    Attributes:
        piece_type (str): Type of piece - 'pawn', 'rook', 'knight', 'bishop', 'queen', 'king'
        color (str): Color of piece - 'white' or 'black'
        position (str): Current position in algebraic notation (e.g., "e4")
    """

    # Unicode chess symbols for display
    UNICODE_SYMBOLS = {
        'white': {
            'king': '♔', 'queen': '♕', 'rook': '♖',
            'bishop': '♗', 'knight': '♘', 'pawn': '♙'
        },
        'black': {
            'king': '♚', 'queen': '♛', 'rook': '♜',
            'bishop': '♝', 'knight': '♞', 'pawn': '♟'
        }
    }

    # ASCII fallback symbols
    ASCII_SYMBOLS = {
        'white': {
            'king': 'K', 'queen': 'Q', 'rook': 'R',
            'bishop': 'B', 'knight': 'N', 'pawn': 'P'
        },
        'black': {
            'king': 'k', 'queen': 'q', 'rook': 'r',
            'bishop': 'b', 'knight': 'n', 'pawn': 'p'
        }
    }

    def __init__(self, piece_type, color, position):
        """
        Initialize a chess piece.

        Args:
            piece_type (str): Type of piece ('pawn', 'rook', 'knight', 'bishop', 'queen', 'king')
            color (str): Color of piece ('white' or 'black')
            position (str): Starting position in algebraic notation (e.g., "e4")

        Raises:
            ValueError: If piece_type or color is invalid
        """
        valid_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        valid_colors = ['white', 'black']

        if piece_type not in valid_types:
            raise ValueError(f"Invalid piece type: {piece_type}. Must be one of {valid_types}")
        if color not in valid_colors:
            raise ValueError(f"Invalid color: {color}. Must be one of {valid_colors}")

        self.piece_type = piece_type
        self.color = color
        self.position = position

    def get_symbol(self, use_unicode=True):
        """
        Get the visual symbol for this piece.

        Args:
            use_unicode (bool): Whether to use Unicode symbols (True) or ASCII fallback (False)

        Returns:
            str: Symbol representing the piece
        """
        if use_unicode:
            return self.UNICODE_SYMBOLS[self.color][self.piece_type]
        else:
            return self.ASCII_SYMBOLS[self.color][self.piece_type]

    def copy(self):
        """
        Create a copy of this piece.

        Returns:
            Piece: A new Piece instance with the same properties
        """
        return Piece(self.piece_type, self.color, self.position)

    def __str__(self):
        """String representation of the piece."""
        return f"{self.color} {self.piece_type} at {self.position}"

    def __repr__(self):
        """Detailed string representation of the piece."""
        return f"Piece('{self.piece_type}', '{self.color}', '{self.position}')"


# Automata Theory Notes for Piece:
# The Piece class represents the entities whose movements are validated by
# the Layer 1 DFAs. Each piece type has its own DFA that defines valid
# transitions (movements) based on the piece's characteristics.