"""
Layer 4: Check-Safety Filter
"""

# Layer 4 validates that moves don't leave own king in check:
# 1. Copy current game state
# 2. Apply proposed move to copy
# 3. Find moving side's king
# 4. Check if any opponent piece can attack that king
# 5. Reuse Layer 1 movement logic for attack detection
# 6. Combine using OR logic: if ANY piece can attack, king is in check
# 7. Reject move if king would be in check, otherwise accept