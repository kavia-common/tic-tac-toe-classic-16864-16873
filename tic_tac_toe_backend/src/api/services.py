"""
Domain services for Tic Tac Toe:
- In-memory repository
- Game engine (rules and AI)
- Orchestrating service
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Literal
import uuid
import random

from .models import GameState, PlayerSymbol, CellValue


WIN_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass
class Game:
    """Internal domain object for a Tic Tac Toe game."""
    game_id: str
    board: List[CellValue] = field(default_factory=lambda: [None] * 9)
    next_player: PlayerSymbol = "X"
    mode: Literal["pvp", "pvc"] = "pvp"
    winner: Optional[PlayerSymbol] = None
    is_draw: bool = False
    is_over: bool = False

    def to_state(self) -> GameState:
        """Convert internal game to API state."""
        return GameState(
            game_id=self.game_id,
            board=self.board.copy(),
            next_player=self.next_player,
            mode=self.mode,
            winner=self.winner,
            is_draw=self.is_draw,
            is_over=self.is_over,
        )


class InMemoryGameRepository:
    """Simple in-memory storage for games. Suitable for demo and tests."""
    def __init__(self) -> None:
        self._store: Dict[str, Game] = {}

    # PUBLIC_INTERFACE
    def create(self, mode: Literal["pvp", "pvc"], player_starts: PlayerSymbol) -> Game:
        """Create and return a new game."""
        game_id = str(uuid.uuid4())
        game = Game(game_id=game_id, board=[None] * 9, next_player=player_starts, mode=mode)
        self._store[game_id] = game
        return game

    # PUBLIC_INTERFACE
    def get(self, game_id: str) -> Optional[Game]:
        """Retrieve a game by ID."""
        return self._store.get(game_id)

    # PUBLIC_INTERFACE
    def save(self, game: Game) -> None:
        """Persist a game instance."""
        self._store[game.game_id] = game


class GameEngine:
    """Game rules, winner detection, and AI."""

    # PUBLIC_INTERFACE
    def check_winner(self, board: List[CellValue]) -> Optional[PlayerSymbol]:
        """Return the winning symbol if any."""
        for a, b, c in WIN_LINES:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None

    # PUBLIC_INTERFACE
    def is_draw(self, board: List[CellValue]) -> bool:
        """Return True if the board is full and no winner."""
        return all(cell is not None for cell in board) and self.check_winner(board) is None

    # PUBLIC_INTERFACE
    def available_moves(self, board: List[CellValue]) -> List[int]:
        """Return a list of indices that are empty."""
        return [i for i, cell in enumerate(board) if cell is None]

    # PUBLIC_INTERFACE
    def make_move(self, board: List[CellValue], position: int, player: PlayerSymbol) -> bool:
        """Place player's mark on the board if valid, return True if successful."""
        if 0 <= position <= 8 and board[position] is None:
            board[position] = player
            return True
        return False

    # PUBLIC_INTERFACE
    def ai_move(self, board: List[CellValue], ai_symbol: PlayerSymbol, human_symbol: PlayerSymbol) -> int:
        """
        Basic but solid AI:
        1. Win if possible.
        2. Block opponent's winning move.
        3. Take center if available.
        4. Take a corner if available.
        5. Take any side.
        Returns chosen position.
        """
        # 1. Winning move
        for pos in self.available_moves(board):
            trial = board.copy()
            trial[pos] = ai_symbol
            if self.check_winner(trial) == ai_symbol:
                return pos

        # 2. Block opponent
        for pos in self.available_moves(board):
            trial = board.copy()
            trial[pos] = human_symbol
            if self.check_winner(trial) == human_symbol:
                return pos

        # 3. Center
        if 4 in self.available_moves(board):
            return 4

        # 4. Corners
        corners = [i for i in [0, 2, 6, 8] if i in self.available_moves(board)]
        if corners:
            return random.choice(corners)

        # 5. Sides
        sides = [i for i in [1, 3, 5, 7] if i in self.available_moves(board)]
        if sides:
            return random.choice(sides)

        # Fallback (shouldn't happen)
        moves = self.available_moves(board)
        return random.choice(moves) if moves else -1


class GameService:
    """Orchestrates repository and engine to provide operations used by API."""
    def __init__(self, repo: InMemoryGameRepository, engine: GameEngine) -> None:
        self.repo = repo
        self.engine = engine

    # PUBLIC_INTERFACE
    def create_game(self, mode: Literal["pvp", "pvc"], player_starts: PlayerSymbol) -> GameState:
        """Create a game and return its initial state."""
        game = self.repo.create(mode=mode, player_starts=player_starts)
        return game.to_state()

    # PUBLIC_INTERFACE
    def get_state(self, game_id: str) -> Optional[GameState]:
        """Return the state of a game if found."""
        game = self.repo.get(game_id)
        return game.to_state() if game else None

    # PUBLIC_INTERFACE
    def make_move(self, game_id: str, position: int, player: PlayerSymbol) -> Tuple[bool, str, Optional[GameState]]:
        """
        Apply a move. When in pvc mode and after a valid human move, AI may respond.
        Returns (valid, reason, state)
        """
        game = self.repo.get(game_id)
        if not game:
            return False, "Game not found", None
        if game.is_over:
            return False, "Game is already over", game.to_state()
        if player != game.next_player:
            return False, "It's not this player's turn", game.to_state()
        if not (0 <= position <= 8):
            return False, "Position must be between 0 and 8", game.to_state()
        if game.board[position] is not None:
            return False, "Cell is already occupied", game.to_state()

        # Player move
        if not self.engine.make_move(game.board, position, player):
            return False, "Invalid move", game.to_state()

        # Update status after player's move
        winner = self.engine.check_winner(game.board)
        if winner:
            game.winner, game.is_over = winner, True
        elif self.engine.is_draw(game.board):
            game.is_draw, game.is_over = True, True
        else:
            # Switch next player
            game.next_player = "O" if game.next_player == "X" else "X"

            # AI move if pvc and game not over and AI's turn
            if game.mode == "pvc" and not game.is_over:
                ai_symbol = game.next_player
                human_symbol = "O" if ai_symbol == "X" else "X"
                ai_pos = self.engine.ai_move(game.board, ai_symbol, human_symbol)
                if ai_pos != -1:
                    self.engine.make_move(game.board, ai_pos, ai_symbol)

                    # Update status after AI move
                    winner = self.engine.check_winner(game.board)
                    if winner:
                        game.winner, game.is_over = winner, True
                    elif self.engine.is_draw(game.board):
                        game.is_draw, game.is_over = True, True
                    else:
                        game.next_player = "O" if ai_symbol == "X" else "X"

        # Persist and return state
        self.repo.save(game)
        return True, "", game.to_state()
