"""Regression tests for atomic castling and move history."""

from app.game_service import GameSession
from app.pgn_service import validate_game_sequence


def test_interactive_castling_creates_one_history_record():
    session = GameSession("castling-history-test")

    # Clear the white kingside castling path.
    session.game_state.board.remove_piece("f1")
    session.game_state.board.remove_piece("g1")

    response = session.make_move("e1", "g1")

    assert response.accepted is True
    assert session.game_state.current_turn == "black"
    assert len(session.game_state.move_history) == 1

    record = session.game_state.move_history[0]
    assert record["is_castling"] is True
    assert record["kingside"] is True
    assert record["from"] == "e1"
    assert record["to"] == "g1"

    assert session.game_state.board.get_piece("g1").piece_type == "king"
    assert session.game_state.board.get_piece("f1").piece_type == "rook"
    assert session.game_state.board.get_piece("e1") is None
    assert session.game_state.board.get_piece("h1") is None

    assert session.game_state.castling_rights["white"] == {
        "kingside": False,
        "queenside": False
    }


def test_coordinate_pgn_castling_is_executed_once():
    moves = [
        "e2e4",
        "e7e5",
        "g1f3",
        "b8c6",
        "f1c4",
        "g8f6",
        "e1g1"
    ]

    valid, processed, steps, failing_move, reason = (
        validate_game_sequence(moves)
    )

    assert valid is True, reason
    assert processed == len(moves)
    assert failing_move is None
    assert len(steps) == len(moves)

    final_fen = steps[-1]["fen_after"]
    fen_parts = final_fen.split()

    assert fen_parts[1] == "b"
    assert fen_parts[2] == "kq"
    assert fen_parts[-1] == "4"

    # White king on g1 and rook on f1.
    assert fen_parts[0].split("/")[-1] == "RNBQ1RK1"


def test_undo_restores_position_before_castling():
    session = GameSession("castling-undo-test")

    session.game_state.board.remove_piece("f1")
    session.game_state.board.remove_piece("g1")

    # Refresh the initial snapshot after preparing the test position.
    session.state_snapshots = [session.game_state.copy()]

    before_fen = session.get_response().fen

    response = session.make_move("e1", "g1")
    assert response.accepted is True
    assert len(session.game_state.move_history) == 1

    success, message, restored = session.undo()

    assert success is True, message
    assert restored.fen == before_fen
    assert restored.current_turn == "white"
    assert restored.move_count == 0
