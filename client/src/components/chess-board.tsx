import { Chessboard } from 'react-chessboard';

interface ChessBoardProps {
  fen: string;
  orientation?: 'white' | 'black';
  width?: number;
  onPieceDrop?: (source: string, target: string) => boolean;
}

export function ChessBoard({ fen, orientation = 'white', width, onPieceDrop }: ChessBoardProps) {
  return (
    <Chessboard
      position={fen}
      boardOrientation={orientation}
      boardWidth={width}
      onPieceDrop={onPieceDrop}
      arePiecesDraggable={false}
      customBoardStyle={{
        borderRadius: '4px',
      }}
      customDarkSquareStyle={{ backgroundColor: '#779952' }}
      customLightSquareStyle={{ backgroundColor: '#edeed1' }}
    />
  );
}
