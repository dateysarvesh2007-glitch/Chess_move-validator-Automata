import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["layers"]) == 4


def test_create_new_game():
    response = client.post("/api/game/new")
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert data["current_turn"] == "white"
    assert "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" in data["fen"]
    assert data["move_count"] == 0


def test_make_valid_move():
    # New game
    new_res = client.post("/api/game/new").json()
    game_id = new_res["game_id"]

    # Play e2 -> e4
    move_res = client.post("/api/game/move", json={
        "game_id": game_id,
        "from_square": "e2",
        "to_square": "e4"
    })
    assert move_res.status_code == 200
    data = move_res.json()
    assert data["accepted"] is True
    assert data["current_turn"] == "black"
    assert data["layer_analysis"]["layer1"]["passed"] is True
    assert data["layer_analysis"]["layer3"]["passed"] is True
    assert data["layer_analysis"]["layer4"]["passed"] is True


def test_reject_wrong_turn_move():
    new_res = client.post("/api/game/new").json()
    game_id = new_res["game_id"]

    # Try moving black pawn on turn 1
    move_res = client.post("/api/game/move", json={
        "game_id": game_id,
        "from_square": "e7",
        "to_square": "e5"
    })
    assert move_res.status_code == 200
    data = move_res.json()
    assert data["accepted"] is False
    assert data["layer_analysis"]["layer3"]["passed"] is False
    assert "belongs to black" in data["reason"].lower()


def test_reject_blocked_path_move():
    new_res = client.post("/api/game/new").json()
    game_id = new_res["game_id"]

    # Try moving bishop through pawn: f1 -> b5
    move_res = client.post("/api/game/move", json={
        "game_id": game_id,
        "from_square": "f1",
        "to_square": "b5"
    })
    assert move_res.status_code == 200
    data = move_res.json()
    assert data["accepted"] is False
    assert data["layer_analysis"]["layer1"]["passed"] is False
    assert "blocked" in data["reason"].lower()


def test_undo_and_reset():
    new_res = client.post("/api/game/new").json()
    game_id = new_res["game_id"]

    # Move 1: e2e4
    client.post("/api/game/move", json={"game_id": game_id, "from_square": "e2", "to_square": "e4"})

    # Undo
    undo_res = client.post("/api/game/undo", json={"game_id": game_id})
    assert undo_res.status_code == 200
    assert undo_res.json()["success"] is True
    assert undo_res.json()["game_state"]["current_turn"] == "white"
    assert undo_res.json()["game_state"]["move_count"] == 0

    # Reset
    reset_res = client.post("/api/game/reset", json={"game_id": game_id})
    assert reset_res.status_code == 200
    assert reset_res.json()["current_turn"] == "white"


def test_validate_sequence():
    seq = ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"]
    res = client.post("/api/game/validate-sequence", json={"moves": seq})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["processed_moves"] == 6


def test_automata_metadata():
    res = client.get("/api/automata/layers")
    assert res.status_code == 200
    data = res.json()
    assert data["total_layers"] == 4

    pieces_res = client.get("/api/automata/pieces")
    assert pieces_res.status_code == 200
    assert "knight" in pieces_res.json()
    assert "rook" in pieces_res.json()


def test_dataset_samples_and_validation():
    samples_res = client.get("/api/dataset/samples")
    assert samples_res.status_code == 200
    samples = samples_res.json()["samples"]
    assert len(samples) > 0

    # Validate legal sample
    val_res = client.post("/api/dataset/validate", json={"sample_id": "game-1"})
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["accepted_games"] == 1
    assert val_data["rejected_games"] == 0
