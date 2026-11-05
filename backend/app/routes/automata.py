from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter(prefix="/api/automata", tags=["automata"])

LAYERS_METADATA = [
    {
        "id": "layer1",
        "name": "Layer 1: Per-Piece Deterministic Finite Automaton (DFA)",
        "formal_definition": "M = (Q, Σ, δ, q₀, F)",
        "description": "Each piece type possesses an independent DFA that validates single-ply geometry, step boundaries, and obstacle obstruction without consulting game history.",
        "states": ["START", "DIRECTION_VERIFIED", "PATH_SCAN", "BLOCKED", "DESTINATION_EVAL", "ACCEPTED", "REJECTED"],
        "alphabet": ["Vector (Δx, Δy)", "Ray cast square states: Empty | Friendly | Enemy", "Boundary predicates: (0 ≤ x,y ≤ 7)"],
        "accepting_condition": "Move matches piece-specific directional grammar, line of sight is clear of intermediate obstacles, and destination does not contain a friendly piece.",
        "rejecting_condition": "Invalid jump/stride vector, collision with friendly piece, or obstacle obstructing sliding ray (Rook, Bishop, Queen).",
        "pieces": ["Rook", "Bishop", "Knight", "Pawn", "King", "Queen"]
    },
    {
        "id": "layer2",
        "name": "Layer 2: History-Dependent Finite State Machine (FSM)",
        "formal_definition": "Extended Mealy/Moore Machine with state vector: S = (h_king, h_rook_k, h_rook_q, last_move_record)",
        "description": "Handles non-local context and temporal constraints that cannot be determined by static board inspection alone.",
        "states": ["BOTH_CASTLE_ELIGIBLE", "KINGSIDE_ONLY", "QUEENSIDE_ONLY", "CASTLING_REVOKED", "EN_PASSANT_ACTIVE", "EN_PASSANT_EXPIRED"],
        "subsystems": [
            {
                "name": "Castling Validator",
                "rules": [
                    "King and designated Rook must have zero prior moves recorded in move history.",
                    "Path between King and Rook must be empty (Layer 1 verification).",
                    "King cannot castle out of check, through check, or into check (Layer 4 cross-verification)."
                ]
            },
            {
                "name": "En Passant Validator",
                "rules": [
                    "Immediate preceding move in sequence must be an enemy pawn advancing exactly 2 squares.",
                    "Moving pawn must be on the 5th rank (for White) or 4th rank (for Black) adjacent to the enemy pawn.",
                    "Capturing pawn moves diagonally to the skipped target square; captured enemy pawn is removed."
                ]
            }
        ],
        "accepting_condition": "Candidate move fulfills historical prerequisites stored in the state memory vector.",
        "rejecting_condition": "King or Rook moved in prior turn, pawn double-step was not the immediately preceding halfmove, or intermediate transit square under attack."
    },
    {
        "id": "layer3",
        "name": "Layer 3: Game Sequence & Turn Alternator FSM",
        "formal_definition": "Sequential Transducer enforcing regular language L = (White_Move · Black_Move)*",
        "description": "Orchestrates full game move streams, ensures strict turn alternation, translates algebraic notations, disambiguates target squares, and maintains chronological board state updates.",
        "states": ["WHITE_TO_MOVE", "BLACK_TO_MOVE", "GAME_OVER_CHECKMATE", "GAME_OVER_DRAW"],
        "alphabet": ["Standard Algebraic Notation (SAN)", "Pure coordinate strings (e2e4)", "Disambiguation qualifiers"],
        "accepting_condition": "Selected piece color strictly matches active state turn, parsed notation resolves to an unambiguous valid candidate move, and lower layers accept.",
        "rejecting_condition": "Out-of-turn play attempt, unparseable notation string, ambiguous piece specification, or lower layer rejection."
    },
    {
        "id": "layer4",
        "name": "Layer 4: King Safety & Check Verification Filter",
        "formal_definition": "Lookahead Invariant Oracle: P(S', King_color) ≡ ¬Attacked(King_pos, S')",
        "description": "Simulates candidate move on a virtual cloned board state, verifies the moving player's king is not left exposed to check, and determines whether check is delivered to the opposing king.",
        "states": ["PRE_SIMULATION", "VIRTUAL_STATE_EVAL", "SELF_CHECK_DETECTED", "SAFE_CHECK_DETECTED", "SAFE_NO_CHECK"],
        "alphabet": ["Virtual board state S'", "Inverse threat ray projection"],
        "accepting_condition": "No enemy piece can legally reach moving player's king coordinate in virtual state S'.",
        "rejecting_condition": "Moving player's king remains or lands in check (pinned piece move, moving king into attacked square, failure to parry existing check)."
    }
]

PIECE_DFAS: Dict[str, Any] = {
    "rook": {
        "piece": "Rook",
        "states": ["START", "CHECK_DIRECTION", "HORIZONTAL_OR_VERTICAL", "CAST_RAY", "OBSTACLE_CHECK", "DESTINATION_EVAL", "ACCEPT", "REJECT"],
        "transition_table": [
            {"from": "START", "input": "Δrow == 0 and Δcol != 0", "to": "HORIZONTAL"},
            {"from": "START", "input": "Δcol == 0 and Δrow != 0", "to": "VERTICAL"},
            {"from": "START", "input": "Δrow != 0 and Δcol != 0", "to": "REJECT_INVALID_DIRECTION"},
            {"from": "HORIZONTAL", "input": "squares between clear", "to": "DESTINATION_EVAL"},
            {"from": "VERTICAL", "input": "squares between clear", "to": "DESTINATION_EVAL"},
            {"from": "CAST_RAY", "input": "any intervening piece found", "to": "REJECT_BLOCKED_PATH"},
            {"from": "DESTINATION_EVAL", "input": "dest is empty or enemy piece", "to": "ACCEPT"},
            {"from": "DESTINATION_EVAL", "input": "dest is friendly piece", "to": "REJECT_FRIENDLY_OCCUPIED"}
        ],
        "viva_insight": "The Rook DFA demonstrates why ray scanning is finite: an 8x8 grid bounds ray length at 7 squares max."
    },
    "bishop": {
        "piece": "Bishop",
        "states": ["START", "CHECK_DIAGONAL", "VALID_DIAGONAL", "CAST_RAY", "OBSTACLE_CHECK", "DESTINATION_EVAL", "ACCEPT", "REJECT"],
        "transition_table": [
            {"from": "START", "input": "|Δrow| == |Δcol| > 0", "to": "VALID_DIAGONAL"},
            {"from": "START", "input": "|Δrow| != |Δcol|", "to": "REJECT_NON_DIAGONAL"},
            {"from": "VALID_DIAGONAL", "input": "diagonal ray squares empty", "to": "DESTINATION_EVAL"},
            {"from": "VALID_DIAGONAL", "input": "intervening piece on diagonal", "to": "REJECT_BLOCKED_PATH"},
            {"from": "DESTINATION_EVAL", "input": "dest empty or enemy", "to": "ACCEPT"},
            {"from": "DESTINATION_EVAL", "input": "dest friendly", "to": "REJECT_FRIENDLY_OCCUPIED"}
        ],
        "viva_insight": "A Bishop is constrained to an invariant square color parity: (row + col) mod 2 is constant across all transitions."
    },
    "knight": {
        "piece": "Knight",
        "states": ["START", "EVAL_L_SHAPE", "DESTINATION_EVAL", "ACCEPT", "REJECT"],
        "transition_table": [
            {"from": "START", "input": "(|Δrow|,|Δcol|) in {(1,2),(2,1)}", "to": "EVAL_L_SHAPE"},
            {"from": "START", "input": "other vector", "to": "REJECT_NON_L_SHAPE"},
            {"from": "EVAL_L_SHAPE", "input": "destination empty or enemy", "to": "ACCEPT"},
            {"from": "EVAL_L_SHAPE", "input": "destination friendly piece", "to": "REJECT_FRIENDLY_OCCUPIED"}
        ],
        "viva_insight": "The Knight DFA has zero ray obstruction transitions because it is permitted to jump over intervening squares."
    },
    "pawn": {
        "piece": "Pawn",
        "states": ["START", "EVAL_DIRECTION", "ONE_STEP_FORWARD", "TWO_STEP_START", "DIAGONAL_CAPTURE", "PROMOTION_CHECK", "ACCEPT", "REJECT"],
        "transition_table": [
            {"from": "START", "input": "backward or sideways", "to": "REJECT_WRONG_DIRECTION"},
            {"from": "START", "input": "1 square forward and dest empty", "to": "PROMOTION_CHECK"},
            {"from": "START", "input": "2 squares forward from initial rank and path clear and dest empty", "to": "ACCEPT"},
            {"from": "START", "input": "1 square diagonal and dest enemy piece", "to": "PROMOTION_CHECK"},
            {"from": "PROMOTION_CHECK", "input": "target rank == 8 (White) or 1 (Black)", "to": "ACCEPT_WITH_PROMOTION"},
            {"from": "PROMOTION_CHECK", "input": "target rank intermediate", "to": "ACCEPT"}
        ],
        "viva_insight": "The Pawn is the only piece whose movement alphabet changes depending on whether the destination square is occupied."
    },
    "queen": {
        "piece": "Queen",
        "states": ["START", "EVAL_DIRECTION", "ROOK_DFA_DELEGATE", "BISHOP_DFA_DELEGATE", "ACCEPT", "REJECT"],
        "transition_table": [
            {"from": "START", "input": "horizontal or vertical move", "to": "ROOK_DFA_DELEGATE"},
            {"from": "START", "input": "diagonal move", "to": "BISHOP_DFA_DELEGATE"},
            {"from": "START", "input": "neither orthogonal nor diagonal", "to": "REJECT_INVALID_DIRECTION"},
            {"from": "ROOK_DFA_DELEGATE", "input": "Rook DFA == ACCEPT", "to": "ACCEPT"},
            {"from": "BISHOP_DFA_DELEGATE", "input": "Bishop DFA == ACCEPT", "to": "ACCEPT"}
        ],
        "viva_insight": "The Queen DFA represents a formal union of the regular languages of the Rook DFA and the Bishop DFA: L(Queen) = L(Rook) ∪ L(Bishop)."
    },
    "king": {
        "piece": "King",
        "states": ["START", "ONE_SQUARE_RANGE", "DESTINATION_EVAL", "ACCEPT", "REJECT"],
        "transition_table": [
            {"from": "START", "input": "max(|Δrow|, |Δcol|) == 1", "to": "ONE_SQUARE_RANGE"},
            {"from": "START", "input": "max(|Δrow|, |Δcol|) > 1 (non-castling)", "to": "REJECT_TOO_FAR"},
            {"from": "ONE_SQUARE_RANGE", "input": "dest empty or enemy", "to": "ACCEPT"},
            {"from": "ONE_SQUARE_RANGE", "input": "dest friendly", "to": "REJECT_FRIENDLY_OCCUPIED"}
        ],
        "viva_insight": "Standard king movement is a strictly local DFA. Castling (2 squares) is handled exclusively by Layer 2's history FSM."
    }
}


@router.get("/layers")
def get_layers_metadata():
    """Return formal specification and metadata for all four automata layers."""
    return {
        "project": "ChessMove Validator",
        "subject": "Theory of Computation / Formal Languages and Automata Theory",
        "total_layers": 4,
        "layers": LAYERS_METADATA
    }


@router.get("/pieces")
def get_all_piece_dfas():
    """Return all piece DFAs with transition matrices."""
    return PIECE_DFAS


@router.get("/piece/{piece_type}")
def get_piece_dfa(piece_type: str):
    """Return detailed DFA specification for a specific piece."""
    key = piece_type.lower()
    if key not in PIECE_DFAS:
        raise HTTPException(status_code=404, detail=f"No DFA found for piece type: {piece_type}")
    return PIECE_DFAS[key]
