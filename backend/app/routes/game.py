from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas import (
    GameStateResponse,
    NewGameResponse,
    MoveRequest,
    MoveResponse,
    ResetRequest,
    UndoRequest,
    UndoResponse,
    SequenceValidateRequest,
    SequenceValidateResponse,
    SequenceValidationStep
)
from app.game_service import session_manager, game_state_to_fen
from app.pgn_service import validate_game_sequence

router = APIRouter(prefix="/api/game", tags=["game"])


@router.post("/new", response_model=NewGameResponse)
def create_new_game(game_id: Optional[str] = None):
    """Create and initialize a new interactive chess game session."""
    session = session_manager.get_or_create(game_id)
    resp = session.reset()
    return NewGameResponse(
        game_id=resp.game_id,
        current_turn=resp.current_turn,
        fen=resp.fen,
        board=resp.board,
        is_check=resp.is_check,
        move_count=resp.move_count,
        castling_rights=resp.castling_rights,
        en_passant_target=resp.en_passant_target,
        move_history=resp.move_history,
        message="New game initialized with standard starting position"
    )


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_state(game_id: str):
    """Fetch the current state of an existing game session."""
    session = session_manager.get_or_create(game_id)
    return session.get_response()


@router.post("/move", response_model=MoveResponse)
def make_move(req: MoveRequest):
    """
    Validate and apply a chess move across all four automata layers.
    Never trusts frontend calculations. Every move is evaluated by the Python engine.
    """
    session = session_manager.get_or_create(req.game_id)
    response = session.make_move(req.from_square.lower(), req.to_square.lower(), req.promotion)
    return response


@router.post("/reset", response_model=GameStateResponse)
def reset_game(req: ResetRequest):
    """Reset the game back to the starting position."""
    session = session_manager.get_or_create(req.game_id)
    return session.reset()


@router.post("/undo", response_model=UndoResponse)
def undo_move(req: UndoRequest):
    """Undo the last valid move made on the board."""
    session = session_manager.get_or_create(req.game_id)
    success, message, state = session.undo()
    return UndoResponse(
        success=success,
        message=message,
        game_state=state
    )


@router.post("/validate-sequence", response_model=SequenceValidateResponse)
def validate_sequence(req: SequenceValidateRequest):
    """
    Validate a complete ordered sequence of moves (coordinate or algebraic notation).
    Demonstrates Layer 3 sequence processing.
    """
    if not req.moves:
        raise HTTPException(status_code=400, detail="Move sequence cannot be empty")

    is_valid, processed_count, step_dicts, failing_move, error_reason = validate_game_sequence(req.moves)

    steps = [SequenceValidationStep(**s) for s in step_dicts]
    final_fen = steps[-1].fen_after if steps else "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    final_turn = "black" if (len(steps) % 2 == 1) else "white"

    return SequenceValidateResponse(
        valid=is_valid,
        total_moves=len(req.moves),
        processed_moves=processed_count,
        final_fen=final_fen,
        final_turn=final_turn,
        steps=steps,
        error_move=failing_move,
        error_reason=error_reason
    )
