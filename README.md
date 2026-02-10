# Regatta

A web-based multiplayer recreation of the 1970 3M board game "Regatta" — a sailboat racing game featuring wind mechanics, tactical positioning, and right-of-way rules.

## About

This is a learning project focused on building a real-world application with Python. The game will support 2-6 players racing yachts around a configurable course, with wind affecting movement speed and strategy.

## Tech Stack

- **Backend:** Python 3.13, FastAPI, PostgreSQL
- **Frontend:** TypeScript, React 19
- **Real-time:** WebSockets

## Status

🚧 In development

## Development

### Prerequisites

- Python 3.13+
- Node.js 22+

### Setup

```bash
# Backend
cd backend
/usr/local/opt/python@3.13/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Frontend
cd frontend
npm install
```

### Commands

All commands run from project root:

| Command | Description |
|---------|-------------|
| `make test-backend` | Run backend tests |
| `make lint-backend` | Lint backend code |
| `make format-backend` | Format backend code |
| `make run-backend` | Start backend server |
| `make test-frontend` | Run frontend tests |
| `make lint-frontend` | Lint frontend code |
| `make format-frontend` | Format frontend code |

## Game Rules

Based on the original 1970 3M Regatta board game.

Key mechanics:

- Wind direction affects movement speed (broad reach fastest, beating slowest)
- Spinnaker cards boost downwind speed
- Puff cards provide tactical advantages
- Blanketing opponents blocks their wind

## License

This project is for personal/educational use. The original Regatta board game is © 3M Company (1970).
