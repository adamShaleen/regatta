import { useRef, MouseEvent } from 'react';
import { Board, BoardProps, CELL_SIZE } from './Board';

interface InteractiveBoardProps extends BoardProps {
  onCellClick: (x: number, y: number) => void;
  onCellHover?: (x: number, y: number) => void;
  disabled?: boolean;
  waitingFor?: string;
}

export const InteractiveBoard = ({
  board,
  yachts,
  onCellClick,
  onCellHover,
  highlightedCell,
  marksRounded,
  cellSize,
  previewPath,
  disabled,
  waitingFor
}: InteractiveBoardProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const cs = cellSize ?? CELL_SIZE;

  const handleClick = (event: MouseEvent<HTMLCanvasElement>) => {
    if (disabled || !canvasRef.current) return;

    const scaleX = canvasRef.current.width / canvasRef.current.offsetWidth;
    const scaleY = canvasRef.current.height / canvasRef.current.offsetHeight;
    const x = Math.floor((event.nativeEvent.offsetX * scaleX) / cs);
    const y = Math.floor((event.nativeEvent.offsetY * scaleY) / cs);

    onCellClick(x, y);
  };

  const handleMouseMove = (event: MouseEvent<HTMLCanvasElement>) => {
    if (disabled || !canvasRef.current || !onCellHover) return;

    const scaleX = canvasRef.current.width / canvasRef.current.offsetWidth;
    const scaleY = canvasRef.current.height / canvasRef.current.offsetHeight;
    const x = Math.floor((event.nativeEvent.offsetX * scaleX) / cs);
    const y = Math.floor((event.nativeEvent.offsetY * scaleY) / cs);

    onCellHover(x, y);
  };

  return (
    <div style={{ position: 'relative' }}>
      <Board
        board={board}
        yachts={yachts}
        highlightedCell={highlightedCell}
        marksRounded={marksRounded}
        cellSize={cellSize}
        previewPath={previewPath}
      />
      <canvas
        style={{ position: 'absolute', top: 0, left: 0, cursor: disabled ? 'default' : 'crosshair' }}
        ref={canvasRef}
        onClick={handleClick}
        onMouseMove={handleMouseMove}
        width={board.grid.width * cs}
        height={board.grid.height * cs}
      />
      {disabled && waitingFor && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(0, 0, 0, 0.35)',
            pointerEvents: 'none'
          }}
        >
          <span
            style={{
              color: 'white',
              fontWeight: 'bold',
              fontSize: '1rem',
              textAlign: 'center',
              textShadow: '0 1px 4px rgba(0,0,0,0.8)'
            }}
          >
            Waiting for {waitingFor}…
          </span>
        </div>
      )}
    </div>
  );
};
