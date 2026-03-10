import { useRef, MouseEvent } from 'react';
import { Board, BoardProps, CELL_SIZE } from './Board';

interface InteractiveBoardProps extends BoardProps {
  onCellClick: (x: number, y: number) => void;
}

export const InteractiveBoard = ({
  board,
  yachts,
  onCellClick
}: InteractiveBoardProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleClick = (event: MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return;

    const scaleX = canvasRef.current.width / canvasRef.current.offsetWidth;
    const scaleY = canvasRef.current.height / canvasRef.current.offsetHeight;
    const x = Math.floor((event.nativeEvent.offsetX * scaleX) / CELL_SIZE);
    const y = Math.floor((event.nativeEvent.offsetY * scaleY) / CELL_SIZE);

    console.log(
      'offsetX:',
      event.nativeEvent.offsetX,
      'offsetY:',
      event.nativeEvent.offsetY
    );

    console.log(
      'canvas.width:',
      canvasRef.current.width,
      'canvas.offsetWidth:',
      canvasRef.current.offsetWidth
    );

    onCellClick(x, y);
  };

  return (
    <div style={{ position: 'relative' }}>
      <Board board={board} yachts={yachts} />
      <canvas
        style={{ position: 'absolute', top: 0, left: 0 }}
        ref={canvasRef}
        onClick={handleClick}
        width={board.grid.width * CELL_SIZE}
        height={board.grid.height * CELL_SIZE}
      />
    </div>
  );
};
