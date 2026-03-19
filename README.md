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
- PostgreSQL (running locally)

### First-Time Setup

**Backend:**

```bash
cd backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create `backend/.env`:

```
DATABASE_URL=postgresql+asyncpg://localhost/regatta
JWT_SECRET_KEY=<generate a random secret>
SHARED_PASSWORD=<choose a password for the app>
```

Create the database and run migrations:

```bash
createdb regatta
createdb regatta_test   # for tests
cd backend && .venv/bin/alembic upgrade head
```

**Frontend:**

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```
VITE_API_URL=http://localhost:8000
```

### Running the App

Start the backend and frontend in separate terminals:

```bash
# Terminal 1 — backend (from project root)
make run-backend

# Terminal 2 — frontend
cd frontend && npm run dev
```

The app will be available at `http://localhost:5173`.

### All Commands

Run from project root unless noted:

| Command                    | Description                      |
| -------------------------- | -------------------------------- |
| `make run-backend`         | Start backend server             |
| `make test-backend`        | Run backend tests                |
| `make lint-backend`        | Lint backend code (ruff)         |
| `make format-backend`      | Format backend code (ruff)       |
| `make typecheck-backend`   | Type-check backend (pyright)     |
| `make test-backend-file FILE=test_foo.py` | Run a single test file |
| `cd frontend && npm run dev`   | Start frontend dev server    |
| `cd frontend && npm run build` | Build frontend for production |
| `cd frontend && npm run lint`  | Lint frontend code           |
| `cd frontend && npm run format` | Format frontend code        |

## Game Rules

Based on the original 1970 3M Regatta board game.

Key mechanics:

- Wind direction affects movement speed (broad reach fastest, beating slowest)
- Spinnaker cards boost downwind speed
- Puff cards provide tactical advantages
- Blanketing opponents blocks their wind

## License

This project is for personal/educational use. The original Regatta board game is © 3M Company (1970).
