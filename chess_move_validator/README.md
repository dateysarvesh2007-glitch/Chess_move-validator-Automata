# Chess Move Legality Checker

## Project Overview
This is a college Theory of Computation / Automata Theory project that implements a chess move legality checker. The program determines whether proposed chess moves are legal and explains why they are accepted or rejected, using concepts from automata theory.

## Four-Layer Architecture

### Layer 1 — Per-piece DFA
Each chess piece type (rook, bishop, knight, pawn, king, queen) has movement-validation logic modeled as a DFA/transition-table system.

### Layer 2 — History-Dependent FSM
This layer handles rules that depend on previous moves, demonstrating why a plain DFA is insufficient:
- Castling rights (tracking king/rook movement history)
- En passant availability (tracking two-square pawn advances)

### Layer 3 — Full Game / Move Sequence Validation
Treats chess moves as an ordered sequence and validates each move by applying Layers 1-4 in sequence.

### Layer 4 — Check-Safety Filter
Ensures moves don't leave the moving player's king in check by reusing Layer 1 movement logic.

## Project Structure
```
chess_move_validator/
│
├── main.py
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── board.py
│   ├── piece.py
│   ├── game_state.py
│   ├── coordinates.py
│   │
│   ├── layer1/         # Per-piece DFAs
│   │   ├── __init__.py
│   │   ├── rook.py
│   │   ├── bishop.py
│   │   ├── knight.py
│   │   ├── pawn.py
│   │   ├── king.py
│   │   └── queen.py
│   │
│   ├── layer2/         # History-dependent FSMs
│   │   ├── __init__.py
│   │   ├── castling.py
│   │   └── en_passant.py
│   │
│   ├── layer3/         # Game sequence validation
│   │   ├── __init__.py
│   │   └── game_validator.py
│   │
│   └── layer4/         # Safety filter and check detection
│       ├── __init__.py
│       ├── safety_filter.py
│       └── check_detector.py
│
└── tests/
    ├── test_coordinates.py
    ├── test_board.py
    ├── test_rook.py
    ├── test_bishop.py
    ├── test_knight.py
    ├── test_pawn.py
    ├── test_king.py
    ├── test_queen.py
    ├── test_castling.py
    ├── test_en_passant.py
    ├── test_check.py
    └── test_game_sequence.py
```

## How to Run
```bash
python main.py
```

## Running Tests
```bash
python -m pytest tests/ -v
```

## Key Features
- Validates all standard chess movements
- Detects blocked paths for sliding pieces
- Handles captures correctly
- Implements turn-based gameplay
- Detects and prevents moves that expose own king to check
- Automatically detects when moves give check (would add + notation)
- Modular design clearly separating automata theory concepts
- Comprehensive test suite

## Automata Theory Concepts Demonstrated
- **Layer 1 (DFA)**: Each piece's movement as a finite state machine
- **Layer 2 (FSM)**: History-dependent rules requiring memory
- **Layer 3 (Sequence)**: Processing ordered sequence of moves
- **Layer 4 (Logic)**: OR combination of attack possibilities for check detection

## Design Notes
- Uses only Python standard library
- Clear separation of concerns between layers
- Extensive comments explaining automata theory connections
- Beginner-friendly code with clear variable names and documentation