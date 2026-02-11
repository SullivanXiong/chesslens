"""
CLI commands for ChessLens chess analysis application.

Provides command-line interface for:
- Fetching games from Chess.com
- Listing recent games
- Triggering analysis (requires API server)
- Generating reports (requires API server and database)
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(name="chesslens", help="Chess analysis powered by Stockfish and AI")
console = Console()


@app.command()
def fetch(
    username: str = typer.Argument(help="Chess.com username to fetch games for"),
):
    """Fetch all games for a Chess.com player and store them locally."""

    async def _fetch():
        import httpx
        from chesslens.services.chess_com_client import ChessComClient
        from chesslens.services.pgn_parser import PgnParser
        from chesslens.services.game_sync_service import GameSyncService

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Fetching games for {username}...", total=None)

            async with httpx.AsyncClient(
                headers={"User-Agent": "ChessLens/1.0 (github.com/SullivanXiong/chesslens)"},
                timeout=30.0,
            ) as http_client:
                client = ChessComClient(http_client)
                sync = GameSyncService(client)

                progress.update(task, description="Fetching player profile...")
                player = await client.get_player(username)
                stats = await client.get_stats(username)

                console.print(f"\n[bold]{player.username}[/bold]")
                console.print(f"  Rapid: {stats.rapid_rating or 'N/A'}")
                console.print(f"  Blitz: {stats.blitz_rating or 'N/A'}")
                console.print(f"  Bullet: {stats.bullet_rating or 'N/A'}")

                progress.update(task, description="Fetching game archives...")
                archives = await client.get_archive_urls(username)
                console.print(f"\n  Archives: {len(archives)} months")

                progress.update(task, description=f"Downloading {len(archives)} archives...")
                all_games = []
                parser = PgnParser()
                for i, url in enumerate(archives):
                    progress.update(task, description=f"Downloading archive {i+1}/{len(archives)}...")
                    monthly = await client.get_monthly_games(url)
                    all_games.extend(monthly)

                progress.update(task, description="Parsing games...")
                parsed = 0
                failed = 0
                for game in all_games:
                    result = parser.parse(game.pgn)
                    if result:
                        parsed += 1
                    else:
                        failed += 1

                progress.update(task, description="Done!")

        console.print(
            f"\n[green]Success![/green] Fetched {len(all_games)} games, parsed {parsed}, failed {failed}"
        )
        console.print(
            f"\n[dim]Note: Run with database to persist games. Use the API server for full functionality.[/dim]"
        )

    asyncio.run(_fetch())


@app.command()
def games(
    username: str = typer.Argument(help="Chess.com username"),
    time_class: str = typer.Option("rapid", help="Filter by time class"),
    limit: int = typer.Option(20, help="Number of games to show"),
):
    """List recent games for a player."""

    async def _games():
        import httpx
        from chesslens.services.chess_com_client import ChessComClient
        from chesslens.services.pgn_parser import PgnParser
        from chesslens.services.game_sync_service import (
            determine_player_result,
            determine_player_color,
        )

        async with httpx.AsyncClient(
            headers={"User-Agent": "ChessLens/1.0 (github.com/SullivanXiong/chesslens)"},
            timeout=30.0,
        ) as http_client:
            client = ChessComClient(http_client)
            parser = PgnParser()

            console.print(f"Fetching games for [bold]{username}[/bold]...")
            all_games = await client.fetch_all_games(username)

            # Filter by time class
            filtered = [g for g in all_games if g.time_class == time_class]
            filtered = filtered[-limit:]  # Last N games
            filtered.reverse()  # Most recent first

            table = Table(title=f"Recent {time_class} games for {username}")
            table.add_column("Date", style="dim")
            table.add_column("Color")
            table.add_column("Opponent")
            table.add_column("Rating")
            table.add_column("Result")
            table.add_column("Opening")
            table.add_column("Moves")

            for game in filtered:
                color = determine_player_color(game, username)
                result = determine_player_result(game, username)
                opponent = game.black_username if color == "white" else game.white_username
                opp_rating = game.black_rating if color == "white" else game.white_rating

                parsed = parser.parse(game.pgn)
                opening = parsed.opening_name[:30] if parsed else "?"
                moves = str(parsed.total_moves // 2) if parsed else "?"

                from datetime import datetime

                date = datetime.fromtimestamp(game.end_time).strftime("%Y-%m-%d")

                result_style = {"win": "green", "loss": "red", "draw": "yellow"}.get(result, "")
                table.add_row(
                    date,
                    color,
                    opponent,
                    str(opp_rating),
                    f"[{result_style}]{result}[/{result_style}]",
                    opening,
                    moves,
                )

            console.print(table)
            console.print(
                f"\nTotal {time_class} games: {len([g for g in all_games if g.time_class == time_class])}"
            )

    asyncio.run(_games())


@app.command()
def analyze(
    game_url: str = typer.Argument(help="Chess.com game URL or game ID"),
):
    """Analyze a single game with Stockfish (via chess-api.com)."""
    console.print("[yellow]Analysis requires the API server to be running.[/yellow]")
    console.print("Start the server with: [bold]make dev-server[/bold]")
    console.print(
        "Then use: [bold]curl -X POST http://localhost:8000/api/analysis/game/{{id}}[/bold]"
    )


@app.command()
def report(
    username: str = typer.Argument(help="Chess.com username"),
):
    """Generate a quick analysis report (requires analyzed games in database)."""
    console.print("[yellow]Full reports require analyzed games in the database.[/yellow]")
    console.print("1. Start the server: [bold]make dev[/bold]")
    console.print(
        "2. Sync games: [bold]curl -X POST http://localhost:8000/api/player/{username}/sync[/bold]"
    )
    console.print("3. Analyze games via the web UI")
    console.print(f"4. View reports at [bold]http://localhost:5173/{username}[/bold]")


if __name__ == "__main__":
    app()
