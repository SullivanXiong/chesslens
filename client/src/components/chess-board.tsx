import { useRef, useState, useEffect } from 'react';
import { Chessboard } from 'react-chessboard';

interface ChessBoardProps {
  fen: string;
  orientation?: 'white' | 'black';
  width?: number;
  onPieceDrop?: (source: string, target: string) => boolean;
}

export function ChessBoard({ fen, orientation = 'white', width, onPieceDrop }: ChessBoardProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [boardWidth, setBoardWidth] = useState(width ?? 480);

  useEffect(() => {
    if (width) return;
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setBoardWidth(Math.floor(entry.contentRect.width));
      }
    });
    observer.observe(el);
    setBoardWidth(Math.floor(el.clientWidth));
    return () => observer.disconnect();
  }, [width]);

  return (
    <div ref={containerRef} className="w-full">
      <Chessboard
        position={fen}
        boardOrientation={orientation}
        boardWidth={boardWidth}
        onPieceDrop={onPieceDrop}
        arePiecesDraggable={false}
        customBoardStyle={{ borderRadius: '4px' }}
        customDarkSquareStyle={{ backgroundColor: '#779952' }}
        customLightSquareStyle={{ backgroundColor: '#edeed1' }}
      />
    </div>
  );
}
