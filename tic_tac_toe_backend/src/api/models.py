"""
Pydantic models (schemas) for Tic Tac Toe API.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


PlayerSymbol = Literal["X", "O"]
CellValue = Optional[PlayerSymbol]  # None, "X", or "O"


class GameState(BaseModel):
    """Represents the current state of a game."""
    game_id: str = Field(..., description="Unique identifier for the game")
    board: List[CellValue] = Field(..., description="Flat 3x3 board as a list of 9 cells")
    next_player: PlayerSymbol = Field(..., description="Symbol of the next player to move")
    mode: Literal["pvp", "pvc"] = Field(..., description="Game mode: player vs player or player vs computer")
    winner: Optional[PlayerSymbol] = Field(None, description="Winner symbol if any")
    is_draw: bool = Field(False, description="Whether the game ended in a draw")
    is_over: bool = Field(False, description="Whether the game is finished")


class CreateGameRequest(BaseModel):
    """Request payload to create a new game."""
    mode: Literal["pvp", "pvc"] = Field(..., description="Game mode: pvp or pvc")
    player_starts: PlayerSymbol = Field("X", description="Symbol that starts the game (X or O)")


class CreateGameResponse(BaseModel):
    """Response after creating a new game."""
    state: GameState = Field(..., description="Initial game state after creation")


class MoveRequest(BaseModel):
    """Request payload to make a move."""
    position: int = Field(..., ge=0, le=8, description="Board index (0-8)")
    player: PlayerSymbol = Field(..., description="The symbol making the move (X or O)")


class MoveOutcome(BaseModel):
    """Outcome details for the move and resulting state."""
    valid: bool = Field(..., description="Whether the move was accepted")
    reason: Optional[str] = Field(None, description="Reason when invalid")
    state: GameState = Field(..., description="Updated game state")
