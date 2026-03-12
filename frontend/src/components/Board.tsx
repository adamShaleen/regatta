import { useEffect, useRef } from 'react';
import { BoardResponse, YachtResponse } from '../types/models';

export interface BoardProps {
  board: BoardResponse;
  yachts: Record<string, YachtResponse>;
  highlightedCell?: { x: number; y: number } | null;
  marksRounded?: { x: number; y: number }[];
}

export const CELL_SIZE = 28;
export const YACHT_COLORS = [
  '#2ecc71',
  '#e67e22',
  '#9b59b6',
  '#00bcd4',
  '#e91e63',
  '#f1c40f'
];

export const Board = ({
  board,
  yachts,
  highlightedCell,
  marksRounded
}: BoardProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const context = canvasRef.current.getContext('2d');
    if (!context) return;

    const drawSailboat = (
      cx: number,
      cy: number,
      color: string,
      heading: number
    ) => {
      const angle = (heading - 90) * (Math.PI / 180);
      context.save();
      context.translate(cx, cy);
      context.rotate(angle);

      const s = CELL_SIZE * 0.4;
      const yo = s * 0.175; // shift down to vertically center the shape

      // sail
      context.beginPath();
      context.moveTo(0, -s * 1.1 + yo);
      context.lineTo(0, s * 0.3 + yo);
      context.lineTo(s * 1.0, s * 0.3 + yo);
      context.closePath();
      context.fillStyle = 'rgba(255, 255, 255, 0.95)';
      context.fill();
      context.strokeStyle = color;
      context.lineWidth = 0.5;
      context.stroke();

      // hull
      context.beginPath();
      context.moveTo(-s * 0.65, s * 0.3 + yo);
      context.lineTo(s * 0.9, s * 0.3 + yo);
      context.lineTo(s * 0.55, s * 0.75 + yo);
      context.lineTo(-s * 0.45, s * 0.75 + yo);
      context.closePath();
      context.fillStyle = color;
      context.fill();
      context.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      context.lineWidth = 1;
      context.stroke();

      context.restore();
    };

    // ocean background
    context.fillStyle = '#1a6b9a';
    context.fillRect(0, 0, canvasRef.current.width, canvasRef.current.height);

    // vertical grid
    context.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    context.lineWidth = 0.5;
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
      const rounded =
        marksRounded?.some((m) => m.x === x && m.y === y) ?? false;
      context.beginPath();
      context.arc(
        x * CELL_SIZE + CELL_SIZE / 2,
        y * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE / 3,
        0,
        Math.PI * 2
      );
      context.fillStyle = rounded ? '#2ecc71' : '#e74c3c';
      context.fill();
      context.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      context.lineWidth = 1.5;
      context.stroke();
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
    context.strokeStyle = '#f1c40f';
    context.lineWidth = 3;
    context.stroke();

    // yachts
    Object.values(yachts).forEach((yacht, index) => {
      const color = YACHT_COLORS[index];
      const { position } = yacht;
      const cx = position.x * CELL_SIZE + CELL_SIZE / 2;
      const cy = position.y * CELL_SIZE + CELL_SIZE / 2;

      drawSailboat(cx, cy, color, yacht.heading);
    });

    if (highlightedCell) {
      context.beginPath();
      context.arc(
        highlightedCell.x * CELL_SIZE + CELL_SIZE / 2,
        highlightedCell.y * CELL_SIZE + CELL_SIZE / 2,
        CELL_SIZE / 3,
        0,
        Math.PI * 2
      );
      context.fillStyle = 'rgba(255, 255, 255, 0.4)';
      context.fill();
    }
  }, [board, yachts, highlightedCell, marksRounded]);

  return (
    <canvas
      ref={canvasRef}
      width={board.grid.width * CELL_SIZE}
      height={board.grid.height * CELL_SIZE}
    />
  );
};
