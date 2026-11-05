import uuid
from typing import Dict, Optional, Tuple, List

try:
    from src.game_state import GameState
    from src.layer3.game_validator import GameValidator
    from src.coordinates import coordinates_to_square, square_to_coordinates
except ImportError:
    from game_state import GameState
    from layer3.game_validator import GameValidator
    from coordinates import coordinates_to_square, square_to_coordinates

from app.schemas import (
    GameStateResponse,
    MoveRecord,
    LayerAnalysis,
    LayerDetail,
    MoveResponse
)


def game_state_to_fen(game_state: GameState) -> str:
    """Generate standard FEN notation from GameState."""
    piece_symbols = {
        ('pawn', 'white'): 'P', ('pawn', 'black'): 'p',
        ('knight', 'white'): 'N', ('knight', 'black'): 'n',
        ('bishop', 'white'): 'B', ('bishop', 'black'): 'b',
        ('rook', 'white'): 'R', ('rook', 'black'): 'r',
        ('queen', 'white'): 'Q', ('queen', 'black'): 'q',
        ('king', 'white'): 'K', ('king', 'black'): 'k',
    }
    fen_ranks = []
    for row in range(7, -1, -1):
        empty_count = 0
        rank_str = ""
        for col in range(8):
            piece = game_state.board.get_piece_at(row, col)
            if piece is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    rank_str += str(empty_count)
                    empty_count = 0
                rank_str += piece_symbols.get((piece.piece_type, piece.color), '?')
        if empty_count > 0:
            rank_str += str(empty_count)
        fen_ranks.append(rank_str)

    board_part = "/".join(fen_ranks)
    turn_part = 'w' if game_state.current_turn == 'white' else 'b'

    # Castling rights
    c_str = ""
    if game_state.castling_rights.get('white', {}).get('kingside'):
        c_str += "K"
    if game_state.castling_rights.get('white', {}).get('queenside'):
        c_str += "Q"
    if game_state.castling_rights.get('black', {}).get('kingside'):
        c_str += "k"
    if game_state.castling_rights.get('black', {}).get('queenside'):
        c_str += "q"
    castling_part = c_str if c_str else "-"

    ep_part = game_state.en_passant_target if game_state.en_passant_target else "-"
    halfmove = 0
    fullmove = len(game_state.move_history) // 2 + 1

    return f"{board_part} {turn_part} {castling_part} {ep_part} {halfmove} {fullmove}"


def game_state_to_board_dict(game_state: GameState) -> Dict[str, str]:
    """Return dictionary mapping square ('e4') to piece code ('wP', 'bK') or empty."""
    piece_map = {
        'pawn': 'P', 'knight': 'N', 'bishop': 'B', 'rook': 'R', 'queen': 'Q', 'king': 'K'
    }
    board_dict = {}
    for row in range(8):
        for col in range(8):
            piece = game_state.board.get_piece_at(row, col)
            square = coordinates_to_square(row, col)
            if piece:
                color_prefix = 'w' if piece.color == 'white' else 'b'
                board_dict[square] = f"{color_prefix}{piece_map.get(piece.piece_type, '')}"
            else:
                board_dict[square] = ""
    return board_dict


def parse_history_records(game_state: GameState) -> List[MoveRecord]:
    """Convert game_state.move_history to schema MoveRecord list."""
    records = []
    for idx, m in enumerate(game_state.move_history, 1):
        piece_name = m.get('piece') or 'piece'
        from_sq = m.get('from', '')
        to_sq = m.get('to', '')
        is_capture = m.get('is_capture', False)
        captured = m.get('captured')
        is_ep = m.get('is_en_passant', False)
        is_promo = m.get('is_promotion', False)
        color = m.get('color', 'white')

        notation = f"{from_sq}{'x' if is_capture else '-'}{to_sq}"
        if is_promo:
            notation += f"={m.get('promotion_piece', 'Q')[0].upper()}"

        records.append(MoveRecord(
            move_number=idx,
            from_square=from_sq,
            to_square=to_sq,
            piece=piece_name,
            color=color,
            notation=notation,
            is_check=False,
            is_capture=is_capture,
            is_en_passant=is_ep,
            is_promotion=is_promo,
            captured=captured
        ))
    return records


class GameSession:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.game_state = GameState()
        self.validator = GameValidator(self.game_state)
        # Store snapshots for undo capability
        self.state_snapshots: List[GameState] = [self.game_state.copy()]

    def get_response(self) -> GameStateResponse:
        return GameStateResponse(
            game_id=self.game_id,
            current_turn=self.game_state.current_turn,
            fen=game_state_to_fen(self.game_state),
            board=game_state_to_board_dict(self.game_state),
            is_check=self._is_active_player_in_check(),
            move_count=len(self.game_state.move_history),
            castling_rights=self.game_state.castling_rights,
            en_passant_target=self.game_state.en_passant_target,
            move_history=parse_history_records(self.game_state)
        )

    def _is_active_player_in_check(self) -> bool:
        """Determine if player whose turn it is is currently in check."""
        try:
            return self.validator.check_detector.is_king_in_check(
                self.game_state, self.game_state.current_turn
            )
        except Exception:
            return False

    def reset(self) -> GameStateResponse:
        self.game_state = GameState()
        self.validator = GameValidator(self.game_state)
        self.state_snapshots = [self.game_state.copy()]
        return self.get_response()

    def undo(self) -> Tuple[bool, str, GameStateResponse]:
        if len(self.state_snapshots) <= 1:
            return False, "Cannot undo from the starting position", self.get_response()

        self.state_snapshots.pop()
        self.game_state = self.state_snapshots[-1].copy()
        self.validator = GameValidator(self.game_state)
        return True, "Previous move undone successfully", self.get_response()

    def make_move(self, from_square: str, to_square: str, promotion: Optional[str] = None) -> MoveResponse:
        current_color = self.game_state.current_turn
        piece = self.game_state.board.get_piece(from_square)

        # Build step-by-step layer diagnostics
        layer1_detail = LayerDetail(name="Layer 1: Per-Piece DFA", passed=True, status="ACCEPTED", details="Geometric step & clear line of sight verified")
        layer2_detail = LayerDetail(name="Layer 2: History FSM", passed=True, status="NOT_APPLICABLE", details="No history-dependent rules required")
        layer3_detail = LayerDetail(name="Layer 3: Game Sequence & Turn FSM", passed=True, status="ACCEPTED", details=f"Active turn ({current_color}) validated")
        layer4_detail = LayerDetail(name="Layer 4: Safety & Check Filter", passed=True, status="ACCEPTED", details="Own king safe after virtual simulation")

        # Basic square format validation
        if not from_square or not to_square or len(from_square) != 2 or len(to_square) != 2:
            layer3_detail.passed = False
            layer3_detail.status = "REJECTED"
            layer3_detail.details = "Invalid square coordinate format"
            return MoveResponse(
                accepted=False,
                reason="Invalid square format specified",
                move_notation="",
                is_check=False,
                current_turn=self.game_state.current_turn,
                fen=game_state_to_fen(self.game_state),
                board=game_state_to_board_dict(self.game_state),
                move_history=parse_history_records(self.game_state),
                layer_analysis=LayerAnalysis(
                    layer1=layer1_detail, layer2=layer2_detail, layer3=layer3_detail, layer4=layer4_detail
                )
            )

        # Check piece ownership & turn
        if piece is None:
            layer3_detail.passed = False
            layer3_detail.status = "REJECTED"
            layer3_detail.details = f"No piece found at {from_square}"
            return MoveResponse(
                accepted=False,
                reason=f"No piece at starting position {from_square}",
                move_notation="",
                is_check=False,
                current_turn=self.game_state.current_turn,
                fen=game_state_to_fen(self.game_state),
                board=game_state_to_board_dict(self.game_state),
                move_history=parse_history_records(self.game_state),
                layer_analysis=LayerAnalysis(
                    layer1=layer1_detail, layer2=layer2_detail, layer3=layer3_detail, layer4=layer4_detail
                )
            )

        if piece.color != current_color:
            layer3_detail.passed = False
            layer3_detail.status = "REJECTED"
            layer3_detail.details = f"Piece belongs to {piece.color}, but active turn is {current_color}"
            return MoveResponse(
                accepted=False,
                reason=f"The {from_square} piece belongs to {piece.color}, not {current_color}",
                move_notation="",
                is_check=False,
                current_turn=self.game_state.current_turn,
                fen=game_state_to_fen(self.game_state),
                board=game_state_to_board_dict(self.game_state),
                move_history=parse_history_records(self.game_state),
                layer_analysis=LayerAnalysis(
                    layer1=layer1_detail, layer2=layer2_detail, layer3=layer3_detail, layer4=layer4_detail
                )
            )

        # Check if castling
        start_col = square_to_coordinates(from_square)[1]
        end_col = square_to_coordinates(to_square)[1]
        is_castling = (piece.piece_type == 'king' and abs(end_col - start_col) == 2)

        # Run core validation via GameValidator
        validation_result = self.validator.validate_move(from_square, to_square)

        if not validation_result['accepted']:
            reason = validation_result['reason']

            # Classify failure to appropriate layer
            if "blocked" in reason.lower() or "cannot move" in reason.lower() or "occupied" in reason.lower() or "invalid" in reason.lower():
                layer1_detail.passed = False
                layer1_detail.status = "REJECTED"
                layer1_detail.details = reason
            elif "castle" in reason.lower() or "passant" in reason.lower():
                layer2_detail.passed = False
                layer2_detail.status = "REJECTED"
                layer2_detail.details = reason
            elif "check" in reason.lower() or "safety" in reason.lower():
                layer4_detail.passed = False
                layer4_detail.status = "REJECTED"
                layer4_detail.details = reason
            else:
                layer1_detail.passed = False
                layer1_detail.status = "REJECTED"
                layer1_detail.details = reason

            return MoveResponse(
                accepted=False,
                reason=reason,
                move_notation="",
                is_check=False,
                current_turn=self.game_state.current_turn,
                fen=game_state_to_fen(self.game_state),
                board=game_state_to_board_dict(self.game_state),
                move_history=parse_history_records(self.game_state),
                layer_analysis=LayerAnalysis(
                    layer1=layer1_detail, layer2=layer2_detail, layer3=layer3_detail, layer4=layer4_detail
                )
            )

        # Move accepted: Apply to game_state if not already castled by validator
        if not is_castling:
            self.game_state.make_move(from_square, to_square)

        # Save snapshot for undo
        self.state_snapshots.append(self.game_state.copy())

        # Layer 2 notes if applicable
        if is_castling:
            layer2_detail.status = "ACCEPTED"
            layer2_detail.details = f"Castling validated against unmoved King/Rook history tape"
        elif piece.piece_type == 'pawn' and abs(end_col - start_col) == 1 and to_square == self.game_state.en_passant_target:
            layer2_detail.status = "ACCEPTED"
            layer2_detail.details = "En passant validated: opponent pawn two-step advance in immediately preceding halfmove"

        is_check = validation_result.get('is_check', False)
        if is_check:
            layer4_detail.details = "Move valid; delivered check to opponent King (+)"

        return MoveResponse(
            accepted=True,
            reason=validation_result['reason'],
            move_notation=validation_result.get('move_notation', f"{from_square}-{to_square}"),
            is_check=is_check,
            is_checkmate=False,
            current_turn=self.game_state.current_turn,
            fen=game_state_to_fen(self.game_state),
            board=game_state_to_board_dict(self.game_state),
            move_history=parse_history_records(self.game_state),
            layer_analysis=LayerAnalysis(
                layer1=layer1_detail, layer2=layer2_detail, layer3=layer3_detail, layer4=layer4_detail
            )
        )


class SessionManager:
    """Manages active user game sessions."""
    def __init__(self):
        self._sessions: Dict[str, GameSession] = {}

    def get_or_create(self, game_id: Optional[str] = None) -> GameSession:
        if not game_id or game_id not in self._sessions:
            new_id = game_id if game_id else str(uuid.uuid4())
            self._sessions[new_id] = GameSession(new_id)
            return self._sessions[new_id]
        return self._sessions[game_id]

    def remove(self, game_id: str):
        if game_id in self._sessions:
            del self._sessions[game_id]


session_manager = SessionManager()
