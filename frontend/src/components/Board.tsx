import { useEffect, useRef } from 'react';
import { BoardResponse, YachtResponse } from '../types/models';

export interface BoardProps {
  board: BoardResponse;
  yachts: Record<string, YachtResponse>;
  highlightedCell?: { x: number; y: number } | null;
  marksRounded?: { x: number; y: number }[];
  cellSize?: number;
  previewPath?: { from: { x: number; y: number }; to: { x: number; y: number } } | null;
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
  marksRounded,
  cellSize,
  previewPath
}: BoardProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Tracks the previous target positions for animation interpolation
  const prevYachtsRef = useRef<Record<string, YachtResponse>>(yachts);
  // Active rAF animation handle
  const animRef = useRef<{ frameId: number } | null>(null);
  // Always holds the latest draw function so the rAF loop picks up prop updates
  const drawFnRef = useRef<((displayYachts: Record<string, YachtResponse>) => void) | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const context = canvasRef.current.getContext('2d');
    if (!context) return;

    const cs = cellSize ?? CELL_SIZE;

    const drawSailboat = (cx: number, cy: number, color: string, heading: number) => {
      const angle = (heading - 90) * (Math.PI / 180);
      context.save();
      context.translate(cx, cy);
      context.rotate(angle);

      const s = cs * 0.4;
      const yo = s * 0.175;

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

    const drawFrame = (displayYachts: Record<string, YachtResponse>) => {
      const canvas = canvasRef.current;
      if (!canvas || !context) return;

      // ocean background
      context.fillStyle = '#1a6b9a';
      context.fillRect(0, 0, canvas.width, canvas.height);

      // vertical grid
      context.strokeStyle = 'rgba(255, 255, 255, 0.15)';
      context.lineWidth = 0.5;
      Array.from(Array(board.grid.width).keys()).forEach((unit) => {
        context.beginPath();
        context.moveTo(unit * cs, 0);
        context.lineTo(unit * cs, board.grid.height * cs);
        context.stroke();
      });

      // horizontal grid
      Array.from(Array(board.grid.height).keys()).forEach((unit) => {
        context.beginPath();
        context.moveTo(0, unit * cs);
        context.lineTo(board.grid.width * cs, unit * cs);
        context.stroke();
      });

      // course marks
      board.course_marks.forEach(({ x, y }) => {
        const rounded = marksRounded?.some((m) => m.x === x && m.y === y) ?? false;
        context.beginPath();
        context.arc(x * cs + cs / 2, y * cs + cs / 2, cs / 3, 0, Math.PI * 2);
        context.fillStyle = rounded ? '#2ecc71' : '#e74c3c';
        context.fill();
        context.strokeStyle = 'rgba(255, 255, 255, 0.8)';
        context.lineWidth = 1.5;
        context.stroke();
      });

      // starting line
      const [start, end] = board.starting_line;
      context.beginPath();
      context.moveTo(start.x * cs + cs / 2, start.y * cs + cs / 2);
      context.lineTo(end.x * cs + cs / 2, end.y * cs + cs / 2);
      context.strokeStyle = '#f1c40f';
      context.lineWidth = 3;
      context.stroke();

      // yachts (using interpolated positions)
      Object.values(displayYachts).forEach((yacht, index) => {
        const color = YACHT_COLORS[index];
        const cx = yacht.position.x * cs + cs / 2;
        const cy = yacht.position.y * cs + cs / 2;
        drawSailboat(cx, cy, color, yacht.heading);
      });

      // preview path (dashed line from current position to destination)
      if (previewPath) {
        context.setLineDash([4, 4]);
        context.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        context.lineWidth = 1.5;
        context.beginPath();
        context.moveTo(previewPath.from.x * cs + cs / 2, previewPath.from.y * cs + cs / 2);
        context.lineTo(previewPath.to.x * cs + cs / 2, previewPath.to.y * cs + cs / 2);
        context.stroke();
        context.setLineDash([]);
      }

      // highlighted destination cell
      if (highlightedCell) {
        context.beginPath();
        context.arc(
          highlightedCell.x * cs + cs / 2,
          highlightedCell.y * cs + cs / 2,
          cs / 3,
          0,
          Math.PI * 2
        );
        context.fillStyle = 'rgba(255, 255, 255, 0.4)';
        context.fill();
      }
    };

    // Always update the ref so the rAF loop uses the latest draw function
    drawFnRef.current = drawFrame;

    // Detect if any yacht positions have changed since last target
    const hasPositionChange = Object.keys(yachts).some((id) => {
      const prev = prevYachtsRef.current[id];
      if (!prev) return true;
      return (
        prev.position.x !== yachts[id].position.x ||
        prev.position.y !== yachts[id].position.y
      );
    });

    if (hasPositionChange) {
      // Cancel any running animation
      if (animRef.current) {
        cancelAnimationFrame(animRef.current.frameId);
        animRef.current = null;
      }

      const startFrom = { ...prevYachtsRef.current };
      // Update ref now so re-renders from non-position changes don't restart animation
      prevYachtsRef.current = yachts;
      const startTime = performance.now();

      const animate = (now: number) => {
        const t = Math.min(1, (now - startTime) / 350);
        const interpolated: Record<string, YachtResponse> = {};
        for (const id of Object.keys(yachts)) {
          const curr = yachts[id];
          const from = startFrom[id] ?? curr;
          interpolated[id] = {
            ...curr,
            position: {
              x: from.position.x + (curr.position.x - from.position.x) * t,
              y: from.position.y + (curr.position.y - from.position.y) * t
            }
          };
        }
        drawFnRef.current?.(interpolated);
        if (t < 1) {
          animRef.current = { frameId: requestAnimationFrame(animate) };
        } else {
          animRef.current = null;
        }
      };

      animRef.current = { frameId: requestAnimationFrame(animate) };
    } else {
      // No position change — redraw immediately if no animation is running
      if (!animRef.current) {
        drawFrame(yachts);
      }
      // If animation is running, the updated drawFnRef will be picked up next frame
    }
  }, [board, yachts, highlightedCell, marksRounded, previewPath, cellSize]);

  // Cancel animation on unmount
  useEffect(() => {
    return () => {
      if (animRef.current) {
        cancelAnimationFrame(animRef.current.frameId);
      }
    };
  }, []);

  const cs = cellSize ?? CELL_SIZE;

  return (
    <canvas
      ref={canvasRef}
      width={board.grid.width * cs}
      height={board.grid.height * cs}
    />
  );
};
