"""
Layer 1: Per-piece Deterministic Finite Automata (DFAs)
"""

# Layer 1 implements movement validation for each piece type as a DFA
# where states represent positions along the path and transitions
# represent conditions like "path clear" or "reached destination"