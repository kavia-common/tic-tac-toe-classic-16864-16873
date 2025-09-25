"""
Game routes for Tic Tac Toe.
"""
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from ..models import CreateGameRequest, CreateGameResponse, GameState, MoveRequest, MoveOutcome
from ..services import InMemoryGameRepository, GameEngine, GameService

router = APIRouter(prefix="/games", tags=["Games"])

# Singletons for simple in-memory application lifetime
_repo = InMemoryGameRepository()
_engine = GameEngine()
_service = GameService(repo=_repo, engine=_engine)


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str = Field(..., description="Error detail message")


@router.post(
    "",
    response_model=CreateGameResponse,
    summary="Create a new game",
    description="""
Create a new Tic Tac Toe game.

- mode: "pvp" (player vs player) or "pvc" (player vs computer)
- player_starts: "X" or "O"
""",
    responses={
        201: {"description": "Game created"},
        422: {"description": "Validation error"},
    },
    status_code=201,
)
# PUBLIC_INTERFACE
def create_game(payload: CreateGameRequest) -> CreateGameResponse:
    """Create a new game and return initial state."""
    state = _service.create_game(mode=payload.mode, player_starts=payload.player_starts)
    return CreateGameResponse(state=state)


@router.get(
    "/{game_id}",
    response_model=GameState,
    summary="Get game state",
    description="Retrieve the current state of a game by its ID.",
    responses={
        200: {"description": "Current game state"},
        404: {"description": "Game not found", "model": ErrorResponse},
    },
)
# PUBLIC_INTERFACE
def get_game_state(
    game_id: str = Path(..., description="ID of the game to fetch"),
) -> GameState:
    """Return the game state by ID."""
    state = _service.get_state(game_id)
    if not state:
        raise HTTPException(status_code=404, detail="Game not found")
    return state


@router.post(
    "/{game_id}/moves",
    response_model=MoveOutcome,
    summary="Make a move",
    description="""
Make a move for the specified game. For 'pvc' mode, the AI will automatically
make its move after a valid human move, if the game is not over.
""",
    responses={
        200: {"description": "Move processed"},
        404: {"description": "Game not found", "model": ErrorResponse},
        409: {"description": "Invalid move", "model": ErrorResponse},
    },
)
# PUBLIC_INTERFACE
def make_move(
    payload: MoveRequest,
    game_id: str = Path(..., description="ID of the game to update"),
) -> MoveOutcome:
    """Apply player move and possibly AI move, returning resulting state and validity."""
    valid, reason, state = _service.make_move(game_id, payload.position, payload.player)
    if state is None:
        raise HTTPException(status_code=404, detail=reason or "Game not found")
    if not valid:
        # Return 200 with valid=False and reason, but also expose 409 via docs
        # to indicate conflict semantics; keeping 200 simplifies client handling.
        return MoveOutcome(valid=False, reason=reason, state=state)
    return MoveOutcome(valid=True, reason=None, state=state)
