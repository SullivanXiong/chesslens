from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://chesslens:chesslens@localhost:5432/chesslens"

    # External APIs
    chess_com_api_base_url: str = "https://api.chess.com/pub"
    chess_api_base_url: str = "https://chess-api.com/v1"
    lichess_explorer_base_url: str = "https://explorer.lichess.ovh"

    # AI Services
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Stockfish
    stockfish_path: str = "/usr/bin/stockfish"

    # App
    app_name: str = "ChessLens"
    debug: bool = False


settings = Settings()
