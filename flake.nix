{
  description = "ChessLens - Chess analysis application";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python311
            uv
            nodejs_20
            nodePackages.pnpm
            stockfish
            postgresql_16
          ];

          shellHook = ''
            export STOCKFISH_PATH="${pkgs.stockfish}/bin/stockfish"
            export DATABASE_URL="postgresql+asyncpg://chesslens:chesslens@localhost:5432/chesslens"

            # Python venv managed by uv
            if [ ! -d ".venv" ]; then
              uv venv .venv
            fi
            source .venv/bin/activate
          '';
        };
      }
    );
}
