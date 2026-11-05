"""
Layer 3: Full Game / Move Sequence Validation
"""

# Layer 3 processes chess moves as an ordered sequence:
# 1. Validate basic movement (Layer 1 DFAs)
# 2. Validate history-dependent rules (Layer 2 FSMs)
# 3. Apply move and update game state
# 4. Check king safety (Layer 4)
# 5. Switch turns and continue to next move