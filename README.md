# ChessMove Validator — Full-Stack Automata-Based Web Application

[![Backend Tests](https://img.shields.io/badge/pytest-100%20passed-emerald)](backend/tests)
[![Frontend Tests](https://img.shields.io/badge/vitest-6%20passed-emerald)](frontend/src/services/api.test.ts)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Theory of Computation](https://img.shields.io/badge/Domain-Automata%20Theory-amber)](frontend/src/pages/AutomataPage.tsx)

A full-stack, deployable web application demonstrating **Formal Language & Automata Theory (Theory of Computation)** through a rule-based chess move legality validator.

> **Academic Note**: This project is **not** a chess-playing bot or minimax search engine. It is a mathematical legality verifier proving how Deterministic Finite Automata (DFAs), History-Dependent Finite State Machines (FSMs), Turn Alternators, and Lookahead Invariant Filters collaborate to recognize legal chess moves.

---

## The Four Validation Layers

```
Move Input (e.g. "e2" -> "e4" or "Nf3")
   │
   ▼
[Layer 3: Game Sequence & Turn Alternator]
   ├── Checks active player turn (White / Black)
   └── Disambiguates Algebraic Notation (SAN)
   │
   ▼
[Layer 1: Per-Piece DFA]
   ├── Evaluates piece-specific geometry (Rook, Bishop, Knight, Pawn, King, Queen)
   └── Validates unobstructed line-of-sight ray tracing
   │
   ▼
[Layer 2: History-Dependent FSM]
   ├── Castling Validator (Verifies King & Rook have 0 prior moves)
   └── En Passant Validator (Verifies enemy pawn 2-square push on preceding ply)
   │
   ▼
[Layer 4: King Safety & Check Filter]
   ├── Simulates move on virtual ephemeral board
   ├── Rejects candidate move if own King remains in check
   └── Determines if candidate move delivers check (+) to opponent King
   │
   ▼
[ACCEPT / REJECT Verdict & State Update]
```

### 1. Layer 1 — Per-Piece DFA
- **Rook**: Horizontal and vertical ray scanning bounded by $7$ squares max.
- **Bishop**: Diagonal ray casting preserving square color parity $((row + col) \bmod 2)$.
- **Knight**: Direct jump vector $(|\Delta row|, |\Delta col|) \in \{(1,2), (2,1)\}$; zero obstacle checks.
- **Pawn**: State machine distinguishing forward moves (empty squares required) from diagonal captures (enemy pieces required) and promotions.
- **Queen**: Formal regular language union: $L(\text{Queen}) = L(\text{Rook}) \cup L(\text{Bishop})$.
- **King**: Local single-square radius (non-castling).

### 2. Layer 2 — History-Dependent FSM
Extends the memoryless DFA with bounded state vectors:
- **Castling Rights**: Tracks irreversible transitions $S \to \emptyset$ whenever King or Rook moves.
- **En Passant**: Ephemeral single-ply window activated by an opponent 2-square pawn push, expiring immediately if not captured.

### 3. Layer 3 — Full Game Sequence Validation
Enforces regular language grammar $L = (\text{White\_Move} \cdot \text{Black\_Move})^*$, prevents out-of-turn moves, parses PGN tokens, and disambiguates candidate pieces.

### 4. Layer 4 — Check-Safety Filter
Simulates proposed moves on a cloned state $S'$. Rejects any move that leaves the moving player's King in check, preventing self-check and enforcing pinned piece constraints.

---

## Technology Stack

- **Backend**:
  - Python 3.11+ / 3.14
  - FastAPI (REST API with OpenAPI documentation)
  - Pydantic v2 (Input schemas and serialization)
  - pytest & anyio (100 automated unit & API test cases)
  - Pure Python validation engine (Zero external chess engine dependencies)
- **Frontend**:
  - React 18 / 19 with Vite & TypeScript
  - Tailwind CSS v4 (Custom Dark Navy `#0a0f1d` and Gold `#f59e0b` palette)
  - `react-chessboard` (Interactive drag-and-drop & click-to-move board)
  - Lucide React (Icons)
  - Vitest (Component and API service unit tests)
- **Deployment**:
  - **Frontend**: Vercel (`vercel.json` SPA configuration)
  - **Backend**: Render (`backend/render.yaml` ASGI configuration)

---

## Project Structure

```
chess_move_validator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app & CORS configuration
│   │   ├── schemas.py           # Pydantic models for moves, games, layers
│   │   ├── game_service.py      # Session management & FEN generator
│   │   ├── pgn_service.py       # PGN parser & Lichess benchmark dataset
│   │   └── routes/
│   │       ├── game.py          # /api/game (new, move, undo, reset, sequence)
│   │       ├── automata.py      # /api/automata (layers, piece DFA specs)
│   │       └── dataset.py       # /api/dataset (samples, batch validation)
│   ├── src/                     # Preserved Python Automata Engine
│   │   ├── board.py, piece.py, coordinates.py, game_state.py
│   │   ├── layer1/              # Piece DFAs
│   │   ├── layer2/              # History FSM
│   │   ├── layer3/              # Game Sequence Validator
│   │   └── layer4/              # Safety Filter & Check Detector
│   ├── tests/                   # 100 pytest tests (91 engine tests + 9 API tests)
│   ├── requirements.txt         # Python dependencies
│   ├── render.yaml              # Render deployment configuration
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/layout/   # Navbar & Footer
│   │   ├── pages/
│   │   │   ├── LandingPage.tsx   # Hero & 4-layer overview
│   │   │   ├── ValidatorPage.tsx # Interactive board & 4-layer decision panel
│   │   │   ├── AutomataPage.tsx  # Interactive DFA state diagrams & viva guide
│   │   │   ├── DatasetPage.tsx   # Lichess PGN testing & negative tests
│   │   │   └── AboutPage.tsx     # TOC thesis documentation
│   │   ├── services/api.ts      # Typed client connected to backend
│   │   ├── index.css            # Dark Navy & Gold theme tokens
│   │   └── App.tsx              # Page router
│   ├── package.json
│   ├── vite.config.ts
│   ├── vercel.json              # Vercel deployment configuration
│   └── .env.example
│
├── .gitignore
└── README.md
```

---

## Local Development Setup

### 1. Backend Setup
```bash
cd backend

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate     # On Windows
# source venv/bin/activate # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run backend development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI interactive documentation will be available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running the Automated Test Suites

### Backend Tests (pytest)
```bash
cd backend
python -m pytest tests/ -v
```
Output: **100 passed in ~1.09s** (all 91 engine unit tests + 9 FastAPI endpoint tests).

### Frontend Tests (vitest)
```bash
cd frontend
npm test
```
Output: **6 passed in ~512ms** (verifying API request construction, response handling, and error states).

### Production Frontend Build
```bash
cd frontend
npm run build
```

---

## Deployment Instructions

### Deploying Frontend to Vercel
1. Push this repository to GitHub.
2. In the [Vercel Dashboard](https://vercel.com), click **Add New Project** and select this repo.
3. Set **Root Directory** to `frontend`.
4. Add Environment Variable:
   - `VITE_API_URL`: Your deployed Render backend URL (e.g. `https://chessmove-validator-backend.onrender.com`).
5. Deploy. Vercel will automatically run `npm run build` using the included `vercel.json`.

### Deploying Backend to Render
1. In the [Render Dashboard](https://render.com), click **New Web Service** and select this repo.
2. Set **Root Directory** to `backend`.
3. Set **Environment** to `Python 3`.
4. Set **Build Command** to: `pip install -r requirements.txt`.
5. Set **Start Command** to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Add Environment Variable:
   - `CORS_ORIGINS`: Your Vercel frontend URL or `*`.

---

## Dataset Attribution & Licensing

- Chess benchmark game sequences are derived from the [Lichess Open Database](https://database.lichess.org/), licensed under **Creative Commons CC0 (Public Domain)**.
- Negative test cases are synthetically generated to verify boundary rejections for Automata Theory course evaluation.
- No bulky PGN datasets are bundled into the client build.

---

## Academic Viva & Oral Defense Highlights

1. **Why is a chess move legality checker an automata theory problem?**
   - It systematically classifies constraints into formal language tiers: memoryless regular languages (DFA for single-piece geometry), finite-memory transducers (FSM for castling/en passant), and lookahead oracles (state simulation for king safety).
2. **Why can't Layer 1 alone decide castling?**
   - Because castling is history-dependent. An inspection of the static 8x8 board cannot reveal if a King moved to e2 and returned to e1 earlier in the game.
3. **How does Layer 4 avoid infinite recursion?**
   - During King safety verification, enemy attack queries only invoke Layer 1 movement and line-of-sight DFA checks, never recursing back into Layer 4.

---

## License
MIT License. Created as a Theory of Computation (TOC) capstone project.
