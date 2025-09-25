# Tic Tac Toe Backend (FastAPI)

Ocean Professional style — Blue (#2563EB) & Amber (#F59E0B) accents.

## Run locally

- Install: `pip install -r requirements.txt`
- Start: `uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload`
- Docs: visit `/docs`

## REST API

- GET `/` — health
- POST `/games` — create a game
  - body: `{ "mode": "pvp" | "pvc", "player_starts": "X" | "O" }`
- GET `/games/{game_id}` — current state
- POST `/games/{game_id}/moves` — make a move
  - body: `{ "position": 0-8, "player": "X" | "O" }`

## Notes

- Games are stored in memory for demo simplicity.
- AI uses a prioritized strategy: win, block, center, corner, side.
