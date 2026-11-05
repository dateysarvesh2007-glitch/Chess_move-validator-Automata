import os
import sys

# Ensure backend directory and engine (src) are in sys.path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
engine_root = os.path.join(backend_root, "src")
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import game, automata, dataset, admin

app = FastAPI(
    title="ChessMove Validator API",
    description="Full-stack rule-based chess move legality validator demonstrating automata theory (Theory of Computation).",
    version="2.0.0"
)

# CORS configuration: Allow Vite dev server and production domains
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(game.router)
app.include_router(automata.router)
app.include_router(dataset.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "service": "ChessMove Validator Engine",
        "version": "2.0.0",
        "layers": ["Layer 1: DFA", "Layer 2: History FSM", "Layer 3: Sequence FSM", "Layer 4: Safety Filter"]
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to ChessMove Validator API",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
