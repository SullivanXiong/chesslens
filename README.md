# ChessLens

Personal chess analysis app that pulls your [Chess.com](https://www.chess.com) game history and provides deep, actionable analysis — playstyle fingerprinting, opening coaching, weakness detection, and an AI-powered chatbot coach.

## Features

- **Game Sync** — Fetch all your games from Chess.com's public API
- **Stockfish Analysis** — Per-move evaluation via cloud Stockfish (chess-api.com)
- **Opening Coach** — Compare your openings against Lichess Explorer book data, find where you leave theory
- **Weakness Detection** — Blunder pattern analysis by game phase, position type, and time pressure
- **Playstyle Classifier** — Fingerprint your play into 6 archetypes (Attacker, Defender, Positional, Speedster, Improviser, Grinder) with a radar chart
- **AI Coaching** — Claude-powered coaching summaries and an interactive chatbot that knows your games
- **CLI + Web UI** — Typer CLI for scripting, React frontend for exploring

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async), Alembic |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Database | PostgreSQL 16, pgvector |
| Chess | python-chess, chess.js, react-chessboard |
| AI | Claude API (coaching + chatbot), OpenAI embeddings (RAG) |
| Analysis | chess-api.com (cloud Stockfish), Lichess Explorer API |
| Charts | Recharts |

## Prerequisites

- **Docker** — for PostgreSQL (via Docker Desktop or Colima)
- **Python 3.11+** and **uv** — for the server
- **Node.js 20+** and **pnpm** — for the client

Or if you use Nix + direnv, everything is provided by the flake:

```bash
direnv allow   # Provides python, uv, node, pnpm, stockfish
```

## Local Setup

### 1. Clone the repository

```bash
git clone git@github.com:SullivanXiong/chesslens.git
cd chesslens
```

### 2. Start PostgreSQL and Redis

```bash
docker compose up -d
```

This starts:
- **PostgreSQL** (pgvector) on port `5432` — user/password/db: `chesslens`
- **Redis** on port `6379`

Verify they're healthy:

```bash
docker compose ps
```

### 3. Configure environment variables

```bash
cp server/.env.example server/.env
```

Edit `server/.env` and fill in your API keys:

```env
# Already set with correct defaults:
DATABASE_URL=postgresql+asyncpg://chesslens:chesslens@localhost:5432/chesslens

# Required for AI coaching + chatbot (optional for basic game fetching/analysis):
ANTHROPIC_API_KEY=sk-ant-...

# Required for RAG embeddings (optional, can skip initially):
OPENAI_API_KEY=sk-...
```

Game fetching, Stockfish analysis, and opening analysis all use free public APIs — no keys needed.

### 4. Install server dependencies

```bash
cd server
uv sync
cd ..
```

### 5. Run database migrations

```bash
cd server
uv run alembic upgrade head
cd ..
```

This creates all tables: `players`, `games`, `move_evaluations`, `analysis_summaries`, `player_analyses`, `chat_messages`, `game_chunk_embeddings`.

### 6. Install client dependencies

```bash
cd client
pnpm install
cd ..
```

### 7. Start the app

Run both the API server and frontend dev server:

```bash
make dev
```

Or run them separately in two terminals:

```bash
# Terminal 1 — API server (port 8000)
cd server && uv run uvicorn chesslens.main:app --reload --port 8000

# Terminal 2 — Frontend dev server (port 5173)
cd client && pnpm dev
```

### 8. Open the app

- **Web UI**: http://localhost:5173
- **API health check**: http://localhost:8000/api/health
- **API docs** (Swagger): http://localhost:8000/docs

## CLI Usage

The CLI provides direct access to core features from the terminal:

```bash
cd server

# Fetch all games for a Chess.com username
uv run chesslens fetch pbr5307

# List fetched games
uv run chesslens games pbr5307

# Analyze a specific game
uv run chesslens analyze <game-id>

# Generate a full player report
uv run chesslens report pbr5307
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/player/{username}` | Get player profile |
| `POST` | `/api/player/{username}/sync` | Sync games from Chess.com |
| `GET` | `/api/player/{username}/games` | List games (paginated, filterable) |
| `GET` | `/api/player/{username}/games/{id}` | Single game with moves |
| `POST` | `/api/analysis/game/{id}` | Trigger Stockfish analysis |
| `GET` | `/api/analysis/game/{id}/status` | Analysis progress |
| `GET` | `/api/analysis/game/{id}/result` | Full per-move evaluations |
| `GET` | `/api/player/{username}/openings` | Opening repertoire report |
| `GET` | `/api/player/{username}/weaknesses` | Weakness analysis |
| `GET` | `/api/player/{username}/playstyle` | Playstyle + radar chart |
| `GET` | `/api/player/{username}/coaching` | AI coaching summary |
| `POST` | `/api/chat` | AI chatbot (SSE streaming) |

## Makefile Commands

```bash
make setup        # docker compose up + uv sync + pnpm install
make dev          # Start both servers
make dev-server   # Start API server only
make dev-client   # Start frontend only
make db-up        # Start Docker containers
make db-down      # Stop Docker containers
make migrate      # Run Alembic migrations
make test         # Run all tests
make format       # Format all code
make lint         # Lint all code
```

## Project Structure

```
chesslens/
├── server/
│   └── src/chesslens/
│       ├── main.py              # FastAPI app
│       ├── config.py            # Settings (env vars)
│       ├── api/                 # Route handlers
│       ├── models/              # ORM models + Pydantic schemas
│       ├── services/            # Chess.com client, PGN parser, analyzers
│       ├── analysis/            # Stockfish eval, move/phase classification
│       ├── rag/                 # Game indexer, retriever, context builder
│       ├── db/                  # Engine, repository, Alembic migrations
│       └── cli/                 # Typer CLI commands
│
├── client/
│   └── src/
│       ├── pages/               # Route pages (home, dashboard, games, etc.)
│       ├── components/          # Board, eval bar, charts, UI primitives
│       ├── hooks/               # TanStack Query hooks
│       ├── store/               # Zustand stores
│       ├── api/                 # Typed API client
│       └── types/               # TypeScript interfaces
│
├── docker-compose.yml           # PostgreSQL + Redis
├── Makefile                     # Dev commands
└── flake.nix                    # Nix dev environment
```
