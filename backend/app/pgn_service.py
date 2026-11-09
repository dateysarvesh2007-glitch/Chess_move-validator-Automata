import re
from typing import List, Dict, Any, Optional, Tuple
from app.game_service import game_state_to_fen

try:
    from src.game_state import GameState
    from src.layer3.game_validator import GameValidator
except ImportError:
    from game_state import GameState
    from layer3.game_validator import GameValidator


SAMPLE_GAMES_METADATA = [
    {
        "id": "game-1",
        "title": "Paul Morphy vs Duke of Brunswick & Count Isouard (The Opera Game, 1858)",
        "white": "Paul Morphy",
        "black": "Duke Karl / Count Isouard",
        "result": "1-0",
        "moves": [
            "e4", "e5", "Nf3", "d6", "d4", "Bg4", "dxe5", "Bxf3", "Qxf3", "dxe5",
            "Bc4", "Nf6", "Qb3", "Qe7", "Nc3", "c6", "Bg5", "b5", "Nxb5", "cxb5",
            "Bxb5+", "Nbd7", "O-O-O", "Rd8", "Rxd7", "Rxd7", "Rd1", "Qe6", "Bxd7+", "Nxd7",
            "Qb8+", "Nxb8", "Rd8#"
        ],
        "category": "legal",
        "description": "One of the most famous games in chess history, featuring aggressive development, queenside castling, pin exploitation, and a queen sacrifice."
    },
    {
        "id": "game-2",
        "title": "Adolf Anderssen vs Lionel Kieseritzky (The Immortal Game, 1851)",
        "white": "Adolf Anderssen",
        "black": "Lionel Kieseritzky",
        "result": "1-0",
        "moves": [
            "e4", "e5", "f4", "exf4", "Bc4", "Qh4+", "Kf1", "b5", "Bxb5", "Nf6",
            "Nf3", "Qh6", "d3", "Nh5", "Nh4", "Qg5", "Nf5", "c6", "g4", "Nf6",
            "Rg1", "cxb5", "h4", "Qg6", "h5", "Qg5", "Qf3", "Ng8", "Bxf4", "Qf6",
            "Nc3", "Bc5", "Nd5", "Qxb2", "Bd6", "Bxg1", "e5", "Qxa1+", "Ke2", "Na6",
            "Nxg7+", "Kd8", "Qf6+", "Nxf6", "Be7#"
        ],
        "category": "legal",
        "description": "Anderssen sacrifices both rooks, a bishop, and his queen to deliver checkmate with three minor pieces."
    },
    {
        "id": "game-3",
        "title": "Evans Gambit Miniature (Lichess Master DB)",
        "white": "Master White",
        "black": "Master Black",
        "result": "1-0",
        "moves": [
            "e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5", "b4", "Bxb4", "c3", "Ba5",
            "d4", "exd4", "O-O", "Qb3", "Qf6", "e5", "Qg6", "Nxc3", "Nge7",
            "Nd5", "Nxd5", "Bxd5", "O-O", "Ba3", "Re8", "Rad1", "Bb6", "Rfe1",
            "Na5", "Qc3", "c6", "Be4", "Qh6", "Bc1", "Qe6", "Ng5", "Qc4", "Qh3",
            "h6", "Bh7+", "Kf8", "Re4", "Qxa2", "Bf5", "Qxf2+", "Kh1", "hxg5",
            "Bxg5", "d5", "Qh8#"
        ],
        "category": "legal",
        "description": "A sharp tactical Evans Gambit game from the open database showcasing castling, bishop pins, and tactical combinations."
    },
    {
        "id": "game-4",
        "title": "Ruy Lopez Classical Opening Sequence",
        "white": "Lichess Rated 2200",
        "black": "Lichess Rated 2185",
        "result": "1/2-1/2",
        "moves": [
            "e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O", "Be7",
            "Re1", "b5", "Bb3", "d6", "c3", "O-O", "h3", "Nb8", "d4", "Nbd7"
        ],
        "category": "legal",
        "description": "Standard Breyer Variation of the Ruy Lopez demonstrating quiet maneuvering, castling, and pawn structure."
    },
    {
        "id": "neg-1",
        "title": "[Negative Test] Self-Check Violation (Layer 4 Violation)",
        "white": "Illegal Player",
        "black": "Checker",
        "result": "REJECTED",
        "moves": [
            "e4", "e5", "Qh5", "g6", "Qxe5+", "Be7", "f3", "Nf6", "Qxe7+"
        ],
        "category": "illegal",
        "description": "White Queen gives check on e5 (Qxe5+); Black attempts to play a non-evasion move or move king into further check."
    },
    {
        "id": "neg-2",
        "title": "[Negative Test] Blocked Sliding Ray (Layer 1 Violation)",
        "white": "Violator",
        "black": "Defender",
        "result": "REJECTED",
        "moves": [
            "f1b5"
        ],
        "category": "illegal",
        "description": "Move 1: White attempts to jump Bishop from f1 to b5 over pawns at e2/d2, verifying that Layer 1 DFA halts in the BLOCKED state."
    },
    {
        "id": "neg-3",
        "title": "[Negative Test] Castling Out of Active Check (Layer 2 Violation)",
        "white": "Check Evader",
        "black": "Attacker",
        "result": "REJECTED",
        "moves": [
            "e4", "e5", "Nf3", "d6", "Bc4", "Bg4", "d3", "Bxf3", "Qxf3", "Qe7",
            "Nc3", "c6", "Bg5", "Nf6", "O-O-O", "Nbd7", "d4", "exd4", "Rxd4", "Qe5",
            "Qe3", "O-O-O"
        ],
        "category": "illegal",
        "description": "Tests castling attempt when intermediate squares or king conditions violate Layer 2 FSM state transitions."
    }
]


def parse_pgn_games(pgn_text: str) -> List[Dict[str, Any]]:
    """
    Lightweight, robust PGN parser written specifically for our rule engine.
    Extracts headers and move list without third-party chess libraries.
    """
    games = []
    # Split PGN by double newlines or event tags
    raw_games = re.split(r'\n(?=\[Event )', pgn_text.strip())

    for raw in raw_games:
        if not raw.strip():
            continue

        headers = {}
        header_lines = re.findall(r'\[(\w+)\s+"([^"]*)"\]', raw)
        for key, val in header_lines:
            headers[key] = val

        # Extract moves section (after the headers)
        body = re.sub(r'\[.*?\]', '', raw).strip()
        # Remove comments {...}
        body = re.sub(r'\{[^}]*\}', '', body)
        # Remove semicolons comments
        body = re.sub(r';.*$', '', body, flags=re.MULTILINE)
        # Remove numeric evaluation glyphs ($1, $2, etc.)
        body = re.sub(r'\$\d+', '', body)

        # Tokenize by whitespace
        tokens = body.split()
        moves = []
        for token in tokens:
            token = token.strip()
            # Skip move numbers like "1.", "2...", etc.
            if re.match(r'^\d+\.+$', token):
                continue
            # If token starts with number like "1.e4", strip the number
            cleaned = re.sub(r'^\d+\.+', '', token)
            # Skip game result markers
            if cleaned in ["1-0", "0-1", "1/2-1/2", "*"]:
                continue
            if cleaned:
                # Strip trailing annotations like ?, !, !?
                cleaned = re.sub(r'[?!]+$', '', cleaned)
                moves.append(cleaned)

        if moves:
            title = f"{headers.get('White', 'Unknown')} vs {headers.get('Black', 'Unknown')}"
            if 'Event' in headers and headers['Event'] != '?':
                title += f" ({headers['Event']})"

            games.append({
                "headers": headers,
                "title": title,
                "moves": moves
            })

    return games


def validate_game_sequence(moves: List[str]) -> Tuple[bool, int, List[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Runs a list of moves sequentially through our project's GameValidator engine.
    Returns: (is_valid, processed_count, step_records, failing_move, error_reason)
    """
    game_state = GameState()
    validator = GameValidator(game_state)
    steps = []

    for idx, move_str in enumerate(moves, 1):
        turn = game_state.current_turn

        try:
            # Check if coordinate format like e2e4 or standard algebraic
            if (len(move_str) == 4 and move_str[0] in 'abcdefgh' and move_str[1] in '12345678' and
                move_str[2] in 'abcdefgh' and move_str[3] in '12345678'):
                from_sq = move_str[:2]
                to_sq = move_str[2:4]
                res = validator.validate_move(from_sq, to_sq)
                if res['accepted']:
                    piece = game_state.board.get_piece(from_sq)
                    start_col = int(ord(from_sq[0]) - ord('a'))
                    end_col = int(ord(to_sq[0]) - ord('a'))
                    is_castling = (
                        piece
                        and piece.piece_type == 'king'
                        and abs(end_col - start_col) == 2
                    )

                    if is_castling:
                        game_state.make_castling_move(
                            turn, end_col > start_col
                        )
                    else:
                        game_state.make_move(from_sq, to_sq)
            else:
                res = validator.parse_and_validate_algebraic_move(move_str)

            if not res['accepted']:
                return False, idx - 1, steps, move_str, res['reason']

            steps.append({
                "move_index": idx,
                "turn": turn,
                "move": move_str,
                "accepted": True,
                "reason": res['reason'],
                "is_check": res.get('is_check', False),
                "fen_after": game_state_to_fen(game_state)
            })

        except Exception as e:
            return False, idx - 1, steps, move_str, f"Validator exception: {str(e)}"

    return True, len(moves), steps, None, None
