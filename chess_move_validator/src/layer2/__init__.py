"""
Layer 2: History-dependent Finite State Machines (FSMs)
"""

# Layer 2 handles rules that depend on game history:
# - Castling rights (tracking king/rook movement)
# - En passant opportunities (tracking double-pawn advances)
# These require memory of previous moves, demonstrating FSM necessity