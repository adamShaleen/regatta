# Regatta Web Game - Project Guide

## Project Overview

A web-based multiplayer recreation of the 1970 3M board game "Regatta" - a sailboat racing game with wind mechanics, tactical positioning, and right-of-way rules.

**Primary Goal:** Learn Python through building a real project.

**Scope:** Private game for friends (controlled access via simple auth).

## Developer Context

- **Experience:** Professional software developer (typescript, javascript, node, react)
- **Learning Focus:** Python
- **Repository:** Public on GitHub for portfolio/learning

## Tech Stack

### Backend

- **Language:** Python
- **Framework:** FastAPI (modern, well-documented)
- **Database:** PostgreSQL (via hosting platform)
- **Real-time:** WebSockets for multiplayer updates

### Frontend

- **Language:** TypeScript
- **Framework:** React
- **Styling:** TBD

### Hosting

- **Backend:** Railway.app (free tier, $5/month credit)
- **Frontend:** Vercel or Netlify (static hosting)
- **Database:** Railway PostgreSQL

### Authentication

- Simple shared password initially (friends-only access)
- Can upgrade to user accounts later

### Version Requirements

- **Python:** 3.13+
- **FastAPI:** 0.115+
- **Pydantic:** 2.x
- **SQLAlchemy:** 2.x (or asyncpg for raw async queries)
- **Node:** 22 LTS (for frontend tooling)
- **React:** 19

## Rules of Engagement for Claude

### Code Assistance

- **DO NOT write code unless explicitly asked**
- When code is requested:
  - Provide concise snippets with applicable comments
  - Explain why this approach over alternatives (best practices)
  - Call out Pythonic conventions vs other languages

### Explanations

- Default to concise answers
- Developer will ask for deep dives when wanted
- Assume web development knowledge (focus on Python-specific concepts)

### Feedback & Suggestions

- **DO** point out non-Pythonic code or potential problems
- **DO** suggest best practices and explain why
- **DO** flag architectural issues or technical debt
- **DO NOT** refactor or rewrite unless asked

### Help Philosophy

Developer will explicitly request help. Claude should:

- Answer what's asked
- Provide context for Python-specific patterns
- Highlight gotchas or common mistakes
- Let developer drive the implementation

## Game Features (Reference)

### Core Mechanics

- Grid-based board with wind direction
- 6 yachts racing around course marks
- Turn-based movement with dice rolls
- Wind affects sailing speed/direction
- Spinnaker cards for speed boosts
- Puff cards for tactical advantages
- Wind shifts change strategy

### Movement System

- **Beating:** 1 space (sailing into wind)
- **Beam reaching/Running:** 2 spaces
- **Broad reaching:** 3 spaces (optimal speed)
- **Luffing:** 0 spaces (dead into wind)

### Advanced Rules (Future)

- Right-of-way rules (port/starboard tack)
- Blanketing (blocking wind)
- Tacking and jibing penalties
- Course mark rounding rules

### Multiplayer Requirements

- 2-6 players per game
- Real-time turn updates
- Game state persistence
- Player authentication
- Game lobby/matchmaking (basic)

## Development Phases

### Phase 1: Core Game Logic (Python)

- Game state representation
- Movement validation
- Wind mechanics
- Turn management
- Basic rules engine

### Phase 2: Database & API

- PostgreSQL schema design
- FastAPI endpoints
- Game CRUD operations
- Player session management

### Phase 3: Real-time Multiplayer

- WebSocket connection management
- Turn synchronization
- State broadcasting
- Connection handling (drops, rejoins)

### Phase 4: Frontend

- Board rendering
- Move input/validation
- Game UI/UX
- Real-time updates from backend

### Phase 5: Polish

- Authentication
- Game history
- Advanced rules
- Visual improvements

## Reference Materials

- Game rules PDF: `regatta_game_rules.pdf`
- BoardGameGeek: https://boardgamegeek.com/boardgame/766/regatta

## Notes

- Build incrementally, test thoroughly
- Prioritize working game over feature completeness
- Can start with simplified rules, add complexity later
- Hot-seat mode could be good first milestone before full multiplayer
