import { PhaseProps } from '../types/models';
import { authFetch } from '../utils/api';
import { InteractiveBoard } from './InteractiveBoard';

const WIND_DIRECTION_LABELS: Record<number, string> = {
  0: 'North',
  45: 'North East',
  90: 'East',
  135: 'South East',
  180: 'South',
  225: 'South West',
  270: 'West',
  315: 'North West'
};

export const SetupPhase = ({ game, setGame, playerId }: PhaseProps) => {
  const handleCellClick = async (x: number, y: number) => {
    const isMyTurn = playerId === game.setup_order[game.current_player_index];
    if (!isMyTurn) return;

    const response = await authFetch(
      `${import.meta.env.VITE_API_URL}/games/${game.id}/starting-position`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_id: playerId, x, y })
      }
    );

    if (!response.ok) {
      const errMsg = `There was an error setting starting position for player ${playerId}`;
      console.error(errMsg);
      throw new Error(errMsg);
    }

    setGame(await response.json());
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="bg-[#1e2d3d] rounded-lg px-6 py-3 flex items-center gap-6">
        <div className="flex flex-col items-center gap-1">
          <span className="text-xs text-gray-400 uppercase tracking-wider">
            Wind
          </span>
          <div className="flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 40 40">
              <g
                transform={`rotate(${(game.wind_direction + 180) % 360}, 20, 20)`}
              >
                <polygon points="20,5 35,35 20,28 5,35" fill="white" />
              </g>
            </svg>
            <span className="text-white font-medium">
              {WIND_DIRECTION_LABELS[game.wind_direction]}
            </span>
          </div>
        </div>

        <div className="w-px h-10 bg-gray-600" />

        <p className="text-white text-sm">
          <span className="font-bold text-yellow-400">
            {game.setup_order[game.current_player_index]}
          </span>
          — click a cell on the starting line to place your yacht
        </p>
      </div>

      <InteractiveBoard
        board={game.board}
        yachts={game.yachts}
        onCellClick={handleCellClick}
      />
    </div>
  );
};
