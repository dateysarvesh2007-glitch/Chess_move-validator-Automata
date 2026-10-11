# Interactive Chess Move Validator

This project provides an interactive chess move validator that implements a four-layer automata theory architecture for move validation.

## Features

- **Four-Layer Architecture**: 
  - Layer 1: Piece-specific DFAs (Deterministic Finite Automata) for basic movement validation
  - Layer 2: History-dependent FSMs (Finite State Machines) for castling and en passant
  - Layer 3: Game sequence validator for turn management and coordination
  - Layer 4: Safety filter for king safety/check detection

- **Interactive Play**: Users can input moves in standard algebraic notation (e.g., e4, Nf3, O-O, exd5)
- **Board Visualization**: Real-time ASCII chess board display after each move
- **Move Validation**: Comprehensive validation using all four layers
- **Move History**: Tracking of all moves made during the game
- **Error Handling**: Clear feedback on why moves are invalid

## Files

- `interactive_chess.py`: Main interactive chess game script
- `demo_interactive.py`: Demonstration script showing automated move validation
- `src/`: Source code containing the four-layer architecture
- `tests/`: Unit tests for all components

## How to Use

### 1. Interactive Play
Run the interactive chess validator:
```bash
python interactive_chess.py
```

Then follow the prompts:
- Enter moves in algebraic notation (e.g., `e4`, `Nf3`, `O-O`, `exd5`)
- Type `board` to see the current board state
- Type `history` to see move history
- Type `reset` to start a new game
- Type `help` to see instructions
- Type `quit` or `exit` to stop the game

### 2. Demonstration
Run the demo script to see automated move validation:
```bash
python demo_interactive.py
```

This shows a sample game sequence with detailed validation output.

## Move Notation Supported

- **Standard moves**: `e4`, `Nf3`, `Be6`, etc.
- **Captures**: `exd5`, `Nxe5`, etc.
- **Castling**: `O-O` (kingside), `O-O-O` (queenside)
- **Pawn promotion**: `e8=Q`, `e8=R`, etc. (basic support)
- **Disambiguation**: `Nbd2`, `R1e3`, etc. (handled by the validator)

## Architecture Details

### Layer 1: Piece-Specific DFAs
Each piece type (pawn, knight, bishop, rook, queen, king) has its own Deterministic Finite Automaton that validates basic movement patterns based on:
- Piece-specific movement rules
- Board occupancy
- Direction constraints
- Special moves (like pawn's two-step initial move)

### Layer 2: History-Dependent FSMs
Finite State Machines handle moves that require historical information:
- Castling validity (depends on king/rook movement history)
- En passant capture (depends on opponent's last move)

### Layer 3: Game Sequence Validator
Coordinates the validation process:
- Determines whose turn it is
- Delegates to appropriate Layer 1 validators
- Delegates to Layer 2 for history-dependent rules
- Applies moves temporarily for safety checking
- Delegates to Layer 4 for king safety validation
- Updates game state and switches turns

### Layer 4: Safety Filter
Validates king safety using:
- Attack detection algorithms
- Check detection
- Pin detection
- Safety validation for potential moves

## Example Game Sequence

Here's how a typical opening sequence would look:

```
Move 1 (white): e2 -> e4
ACCEPTED: Legal two-square pawn advance from starting rank
[Board updates]
Current turn: black

Move 2 (black): e7 -> e5
ACCEPTED: Legal two-square pawn advance from starting rank
[Board updates]
Current turn: white

Move 3 (white): g1 -> f3
ACCEPTED: Legal knight move from g1 to f3
[Board updates]
Current turn: black
```

## Requirements

- Python 3.x
- No external dependencies (uses only standard library)

## Testing

Run the unit tests to verify all components work correctly:
```bash
python -m unittest discover tests/
```

## Design Philosophy

This implementation demonstrates how automata theory concepts can be applied to solve complex, real-world problems by:
1. Separating concerns into layers matching computational complexity
2. Using the simplest adequate computational model for each concern
3. Composing layers to handle increasingly complex requirements
4. Providing clear interfaces between layers for maintainability