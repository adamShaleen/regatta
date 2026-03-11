import { useNavigate } from 'react-router';
import { PhaseProps } from '../types/models';
import { Board, CELL_SIZE, YACHT_COLORS } from './Board';

export const FinishedPhase = ({ game }: PhaseProps) => {
  const navigate = useNavigate();
  const winnerIndex = game.winner
    ? Object.keys(game.yachts).indexOf(game.winner)
    : -1;
  const winnerColor =
    winnerIndex >= 0 ? YACHT_COLORS[winnerIndex] : 'white';

  return (
    <div
      className="flex flex-col items-center gap-4"
      style={{ width: game.board.grid.width * CELL_SIZE }}
    >
      <Board board={game.board} yachts={game.yachts} />

      <div className="flex items-center justify-between bg-[#1e2d3d] px-8 py-4 w-full">
        <div className="flex items-center gap-6">
          <span className="text-yellow-400 text-sm font-bold tracking-widest uppercase">
            Winner
          </span>
          <span className="font-bold text-xl" style={{ color: winnerColor }}>
            {game.winner ?? '—'}
          </span>
        </div>
        <button
          onClick={() => navigate('/')}
          className="bg-yellow-400 hover:bg-yellow-300 text-gray-900 font-bold px-6 py-2 rounded-lg tracking-wider transition-colors"
        >
          NEW GAME
        </button>
      </div>
    </div>
  );
};
