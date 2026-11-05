from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from app.schemas import (
    DatasetValidateRequest,
    DatasetValidateResponse,
    DatasetGameResult
)
from app.pgn_service import (
    SAMPLE_GAMES_METADATA,
    parse_pgn_games,
    validate_game_sequence
)

router = APIRouter(prefix="/api/dataset", tags=["dataset"])


@router.get("/samples")
def get_dataset_samples():
    """List preloaded Lichess Open Database games and negative test cases."""
    return {
        "dataset_name": "Lichess Open Database & Automated Negative Test Suite",
        "license": "Creative Commons CC0 (Public Domain)",
        "source": "https://database.lichess.org/",
        "attribution": "Standard chess games from Lichess Open Database and custom negative test cases for Automata Theory verification.",
        "total_samples": len(SAMPLE_GAMES_METADATA),
        "samples": [
            {
                "id": g["id"],
                "title": g["title"],
                "white": g["white"],
                "black": g["black"],
                "result": g["result"],
                "move_count": len(g["moves"]),
                "category": g["category"],
                "description": g["description"]
            }
            for g in SAMPLE_GAMES_METADATA
        ]
    }


@router.post("/validate", response_model=DatasetValidateResponse)
def validate_dataset(req: DatasetValidateRequest):
    """
    Validate selected sample games or custom PGN string through the project's Python validation engine.
    Produces comprehensive testing statistics and failure diagnostics.
    """
    games_to_test = []

    # If specific sample requested
    if req.sample_id:
        target = next((g for g in SAMPLE_GAMES_METADATA if g["id"] == req.sample_id), None)
        if not target:
            raise HTTPException(status_code=404, detail=f"Sample game {req.sample_id} not found")
        games_to_test.append({
            "id": target["id"],
            "title": target["title"],
            "moves": target["moves"],
            "metadata": {
                "White": target["white"],
                "Black": target["black"],
                "Result": target["result"],
                "Category": target["category"]
            }
        })
    elif req.pgn_content and req.pgn_content.strip():
        # User uploaded custom PGN
        parsed = parse_pgn_games(req.pgn_content)
        if not parsed:
            raise HTTPException(status_code=400, detail="Unable to extract valid games or moves from uploaded PGN text")
        for idx, p in enumerate(parsed, 1):
            games_to_test.append({
                "id": f"upload-{idx}",
                "title": p["title"],
                "moves": p["moves"],
                "metadata": p["headers"]
            })
    else:
        # Test sample library based on filter
        for g in SAMPLE_GAMES_METADATA:
            if req.test_type == "all" or req.test_type == g["category"]:
                games_to_test.append({
                    "id": g["id"],
                    "title": g["title"],
                    "moves": g["moves"],
                    "metadata": {
                        "White": g["white"],
                        "Black": g["black"],
                        "Result": g["result"],
                        "Category": g["category"]
                    }
                })

    game_results: List[DatasetGameResult] = []
    total_moves_processed = 0
    accepted_games_count = 0
    rejected_games_count = 0

    for g in games_to_test:
        moves = g["moves"]
        is_valid, processed_count, steps, failing_move, error_reason = validate_game_sequence(moves)
        total_moves_processed += processed_count

        status = "ACCEPTED" if is_valid else "REJECTED"
        if is_valid:
            accepted_games_count += 1
        else:
            rejected_games_count += 1

        game_results.append(DatasetGameResult(
            id=g["id"],
            title=g["title"],
            total_moves=len(moves),
            processed_moves=processed_count,
            status=status,
            reason=error_reason if not is_valid else "All moves verified legal through 4-layer engine",
            failing_move=failing_move,
            metadata=g["metadata"]
        ))

    return DatasetValidateResponse(
        dataset_name="Lichess Verified Dataset & Negative Test Suite",
        total_games=len(games_to_test),
        accepted_games=accepted_games_count,
        rejected_games=rejected_games_count,
        total_moves=total_moves_processed,
        games=game_results
    )
