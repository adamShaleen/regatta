import { useEffect, useRef } from 'react';
import { BoardResponse, YachtResponse } from '../types/models';

export interface BoardProps {
  board: BoardResponse;
  yachts: Record<string, YachtResponse>;
}

export const CELL_SIZE = 24;
export const YACHT_COLORS = [
  'green',
  'orange',
  'purple',
  'cyan',
  'magenta',
  'yellow'
];

export const Board = ({ board, yachts }: BoardProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const context = canvasRef.current.getContext('2d');
    if (!context) return;

    // vertical grid
    Array.from(Array(board.grid.width).keys()).forEach((unit) => {
      context.beginPath();
      context.moveTo(unit * CELL_SIZE, 0);
      context.lineTo(unit * CELL_SIZE, board.grid.height * CELL_SIZE);
      context.stroke();
    });

    // horizontal grid
    Array.from(Array(board.grid.height).keys()).forEach((unit) => {
      context.beginPath();
      context.moveTo(0, unit * CELL_SIZE);
      context.lineTo(board.grid.width * CELL_SIZE, unit * CELL_SIZE);
      context.stroke();
    });

    // course marks
    board.course_marks.forEach(({ x, y }) => {
      context.beginPath();
      context.arc(
        x * CELL_SIZE + CELL_SIZE / 2,
        y * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE / 3,
        0,
        Math.PI * 2
      );
      context.fillStyle = 'red';
      context.fill();
    });

    // starting line
    const [start, end] = board.starting_line;
    context.beginPath();
    context.moveTo(
      start.x * CELL_SIZE + CELL_SIZE / 2,
      start.y * CELL_SIZE + CELL_SIZE / 2
    );
    context.lineTo(
      end.x * CELL_SIZE + CELL_SIZE / 2,
      end.y * CELL_SIZE + CELL_SIZE / 2
    );
    context.strokeStyle = 'blue';
    context.lineWidth = 3;
    context.stroke();
    context.strokeStyle = 'black';
    context.lineWidth = 1;

    // yachts
    Object.values(yachts).forEach((yacht, index) => {
      const color = YACHT_COLORS[index];
      const { position } = yacht;

      context.beginPath();
      context.arc(
        position.x * CELL_SIZE + CELL_SIZE / 2,
        position.y * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE / 3,
        0,
        Math.PI * 2
      );
      context.fillStyle = color;
      context.fill();
    });
  }, [board, yachts]);

  return (
    <canvas
      ref={canvasRef}
      width={board.grid.width * CELL_SIZE}
      height={board.grid.height * CELL_SIZE}
    />
  );
};
