from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LayerDetail(BaseModel):
    name: str
    passed: bool
    status: str  # "ACCEPTED", "REJECTED", "NOT_APPLICABLE"
    details: str


class LayerAnalysis(BaseModel):
    layer1: LayerDetail
    layer2: LayerDetail
    layer3: LayerDetail
    layer4: LayerDetail


class MoveRecord(BaseModel):
    move_number: int
    from_square: str
    to_square: str
    piece: str
    color: str
    notation: str
    is_check: bool
    is_capture: bool
    is_en_passant: bool
    is_promotion: bool
    captured: Optional[str] = None


class GameStateResponse(BaseModel):
    game_id: str
    current_turn: str
    fen: str
    board: Dict[str, str]
    is_check: bool
    move_count: int
    castling_rights: Dict[str, Dict[str, bool]]
    en_passant_target: Optional[str] = None
    move_history: List[MoveRecord] = []


class NewGameResponse(GameStateResponse):
    message: str = "New game initialized successfully"


class MoveRequest(BaseModel):
    game_id: str
    from_square: str = Field(..., description="Source square, e.g. e2")
    to_square: str = Field(..., description="Destination square, e.g. e4")
    promotion: Optional[str] = Field(None, description="Promotion piece, e.g. queen")


class MoveResponse(BaseModel):
    accepted: bool
    reason: str
    move_notation: str
    is_check: bool
    is_checkmate: bool = False
    current_turn: str
    fen: str
    board: Dict[str, str]
    move_history: List[MoveRecord]
    layer_analysis: LayerAnalysis


class ResetRequest(BaseModel):
    game_id: str


class UndoRequest(BaseModel):
    game_id: str


class UndoResponse(BaseModel):
    success: bool
    message: str
    game_state: GameStateResponse


class SequenceValidateRequest(BaseModel):
    moves: List[str] = Field(..., description="List of algebraic or coordinate moves")


class SequenceValidationStep(BaseModel):
    move_index: int
    turn: str
    move: str
    accepted: bool
    reason: str
    is_check: bool
    fen_after: str


class SequenceValidateResponse(BaseModel):
    valid: bool
    total_moves: int
    processed_moves: int
    final_fen: str
    final_turn: str
    steps: List[SequenceValidationStep]
    error_move: Optional[str] = None
    error_reason: Optional[str] = None


class DatasetGameResult(BaseModel):
    id: str
    title: str
    total_moves: int
    processed_moves: int
    status: str  # "ACCEPTED", "REJECTED"
    reason: Optional[str] = None
    failing_move: Optional[str] = None
    metadata: Dict[str, str]


class DatasetValidateRequest(BaseModel):
    sample_id: Optional[str] = None
    pgn_content: Optional[str] = None
    test_type: Optional[str] = "all"  # "all", "legal", "illegal"


class DatasetValidateResponse(BaseModel):
    dataset_name: str
    total_games: int
    accepted_games: int
    rejected_games: int
    total_moves: int
    games: List[DatasetGameResult]
