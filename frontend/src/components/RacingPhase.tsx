import { useState } from 'react';
import { PhaseProps } from '../types/models';
import { CELL_SIZE, YACHT_COLORS } from './Board';
import { InteractiveBoard } from './InteractiveBoard';
import { authFetch } from '../utils/api';

const HEADING_MAP: Record<string, number> = {
  '0,-1': 0, // NORTH
  '1,-1': 45, // NORTH_EAST
  '1,0': 90, // EAST
  '1,1': 135, // SOUTH_EAST
  '0,1': 180, // SOUTH
  '-1,1': 225, // SOUTH_WEST
  '-1,0': 270, // WEST
  '-1,-1': 315 // NORTH_WEST
};

const HEADING_DELTAS: Record<number, { dx: number; dy: number }> = {
  0: { dx: 0, dy: -1 },
  45: { dx: 1, dy: -1 },
  90: { dx: 1, dy: 0 },
  135: { dx: 1, dy: 1 },
  180: { dx: 0, dy: 1 },
  225: { dx: -1, dy: 1 },
  270: { dx: -1, dy: 0 },
  315: { dx: -1, dy: -1 }
};

const ANGLE_TO_SPEED: Record<number, number> = {
  0: 0,
  45: 1,
  90: 2,
  135: 3,
  180: 2
};

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

export const RacingPhase = ({ game, setGame, playerId }: PhaseProps) => {
  const currentPlayer = game.setup_order[game.current_player_index];
  const currentPlayerPosition = game.yachts[currentPlayer];
  const colorIndex = Object.keys(game.yachts).indexOf(currentPlayer);
  const isMyTurn = playerId === game.setup_order[game.current_player_index];

  const [highlightedCell, setHighlightedCell] = useState<{
    x: number;
    y: number;
  } | null>(null);

  const [showRules, setShowRules] = useState(false);
  const [puffMode, setPuffMode] = useState(false);

  const raiseSpinnaker = async () => {
    if (!isMyTurn) return false;
    const response = await authFetch(
      `${import.meta.env.VITE_API_URL}/games/${game.id}/spinnaker/raise`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_id: currentPlayer })
      }
    );

    if (!response.ok) {
      const errMsg = `There was an error raising spinnaker for player ${currentPlayer}`;
      console.error(errMsg);
      throw new Error(errMsg);
    }

    setGame(await response.json());
  };

  const lowerSpinnaker = async () => {
    if (!isMyTurn) return false;

    const response = await authFetch(
      `${import.meta.env.VITE_API_URL}/games/${game.id}/spinnaker/lower`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_id: currentPlayer })
      }
    );

    if (!response.ok) {
      const errMsg = `There was an error lowering spinnaker for player ${currentPlayer}`;
      console.error(errMsg);
      throw new Error(errMsg);
    }

    setGame(await response.json());
  };

  const startRound = async () => {
    if (!isMyTurn) return false;

    const response = await authFetch(
      `${import.meta.env.VITE_API_URL}/games/${game.id}/round`,
      { method: 'POST' }
    );

    if (!response.ok) {
      const errMsg = `There was an error starting the round for gameId ${game.id}`;
      console.error(errMsg);
      throw new Error(errMsg);
    }

    setGame(await response.json());
  };

  const handleCellClick = async (x: number, y: number) => {
    if (!isMyTurn) return false;

    const dx = x - currentPlayerPosition.position.x;
    const dy = y - currentPlayerPosition.position.y;

    const heading = HEADING_MAP[`${Math.sign(dx)},${Math.sign(dy)}`];
    if (heading === undefined) return;

    if (puffMode) {
      const response = await authFetch(
        `${import.meta.env.VITE_API_URL}/games/${game.id}/puff`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ player_id: currentPlayer, direction: heading })
        }
      );

      if (!response.ok) {
        const errMsg = `There was an error using puff for player ${currentPlayer}`;
        console.error(errMsg);
        throw new Error(errMsg);
      }

      setGame(await response.json());
      setHighlightedCell(null);
      setPuffMode(false);
      return;
    }

    const response = await authFetch(
      `${import.meta.env.VITE_API_URL}/games/${game.id}/move`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: game.setup_order[game.current_player_index],
          heading
        })
      }
    );

    if (!response.ok) {
      const errMsg = `There was an error selecting position for player ${game.setup_order[game.current_player_index]}`;
      console.error(errMsg);
      throw new Error(errMsg);
    }

    setGame(await response.json());
    setHighlightedCell(null);
  };

  const handleCellHover = (x: number, y: number) => {
    if (!isMyTurn) return false;

    const dx = x - currentPlayerPosition.position.x;
    const dy = y - currentPlayerPosition.position.y;

    const heading = HEADING_MAP[`${Math.sign(dx)},${Math.sign(dy)}`];

    if (heading === undefined) {
      setHighlightedCell(null);
      return;
    }

    // In puff mode, any adjacent cell is valid (wind ignored, always 1 space)
    if (puffMode) {
      const { dx: stepX, dy: stepY } = HEADING_DELTAS[heading];
      setHighlightedCell({
        x: currentPlayerPosition.position.x + stepX,
        y: currentPlayerPosition.position.y + stepY
      });
      return;
    }

    const angle = Math.min(
      Math.abs(game.wind_direction - heading),
      360 - Math.abs(game.wind_direction - heading)
    );

    const speed = ANGLE_TO_SPEED[angle];

    if (speed === 0) {
      setHighlightedCell(null);
      return;
    }

    const { dx: stepX, dy: stepY } = HEADING_DELTAS[heading];
    const destX = currentPlayerPosition.position.x + stepX * speed;
    const destY = currentPlayerPosition.position.y + stepY * speed;
    setHighlightedCell({ x: destX, y: destY });
  };

  return (
    <div
      className="flex flex-col items-center gap-4"
      style={{ width: game.board.grid.width * CELL_SIZE }}
    >
      <InteractiveBoard
        board={game.board}
        yachts={game.yachts}
        onCellClick={handleCellClick}
        onCellHover={handleCellHover}
        highlightedCell={highlightedCell}
        marksRounded={game.yachts[currentPlayer].marks_rounded}
      />

      <div className="flex flex-col gap-3 bg-[#1e2d3d] px-8 py-4 w-full overflow-hidden">
        <div className="flex items-center justify-center gap-8">
          <div className="flex flex-col items-center justify-between min-h-14">
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

          <div className="w-px h-14 bg-gray-600" />

          <div className="flex flex-col items-center justify-between min-h-14">
            <span className="text-xs text-gray-400 uppercase tracking-wider">
              Current Player
            </span>
            <span
              className="font-bold text-lg"
              style={{ color: YACHT_COLORS[colorIndex] }}
            >
              {game.setup_order[game.current_player_index]}
            </span>
          </div>

          <div className="w-px h-14 bg-gray-600" />

          <div className="flex flex-col items-center justify-between min-h-14">
            <span className="text-xs text-gray-400 uppercase tracking-wider text-center">
              {game.setup_order[game.current_player_index]}
              <br />
              Legs Remaining
            </span>
            <span className="text-white font-bold text-lg">
              {game.legs_remaining}
            </span>
          </div>

          {game.legs_remaining === 0 && (
            <>
              <div className="w-px h-10 bg-gray-600" />
              <button
                disabled={!isMyTurn}
                onClick={startRound}
                className="bg-yellow-400 hover:bg-yellow-300 text-gray-900 font-bold px-6 py-2 rounded-lg tracking-wider transition-colors"
              >
                START ROUND
              </button>
            </>
          )}

          {game.legs_remaining > 0 && (
            <>
              <div className="w-px h-10 bg-gray-600" />
              {game.yachts[currentPlayer].spinnaker ? (
                <button
                  disabled={!isMyTurn}
                  onClick={lowerSpinnaker}
                  className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-lg tracking-wider transition-colors"
                >
                  LOWER SPINNAKER
                </button>
              ) : (
                <button
                  disabled={!isMyTurn}
                  onClick={raiseSpinnaker}
                  className="bg-blue-600 hover:bg-blue-500 text-white font-bold px-4 py-2 rounded-lg tracking-wider transition-colors"
                >
                  RAISE SPINNAKER
                </button>
              )}

              {!game.has_used_puff &&
                game.yachts[currentPlayer].puff_count > 0 && (
                  <>
                    <div className="w-px h-10 bg-gray-600" />
                    <button
                      disabled={!isMyTurn}
                      onClick={() => setPuffMode((v) => !v)}
                      className={`font-bold px-4 py-2 rounded-lg tracking-wider transition-colors ${
                        puffMode
                          ? 'bg-yellow-400 text-gray-900'
                          : 'bg-blue-600 hover:bg-blue-500 text-white'
                      }`}
                    >
                      USE PUFF ({game.yachts[currentPlayer].puff_count})
                    </button>
                  </>
                )}
            </>
          )}
        </div>

        <div className="border-t border-gray-700 pt-3 flex items-center justify-between">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
            <span className="text-xs text-gray-400 uppercase tracking-wider mr-2">
              Legend
            </span>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#e74c3c] border border-white/50" />
              <span className="text-xs text-gray-300">Course Mark</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-5 h-0.5 bg-yellow-400" />
              <span className="text-xs text-gray-300">Start / Finish</span>
            </div>
            {Object.keys(game.yachts).map((playerId, index) => (
              <div key={playerId} className="flex items-center gap-1.5">
                <svg width="28" height="25" viewBox="0 0 18 16">
                  <polygon
                    points="8,3.4 8,10.4 13,10.4"
                    fill="rgba(255,255,255,0.95)"
                    stroke={YACHT_COLORS[index]}
                    strokeWidth="0.5"
                  />
                  <polygon
                    points="4.75,10.4 12.5,10.4 10.75,12.6 5.75,12.6"
                    fill={YACHT_COLORS[index]}
                    stroke="rgba(255,255,255,0.8)"
                    strokeWidth="0.8"
                  />
                </svg>
                <span className="text-xs text-gray-300">{playerId}</span>
              </div>
            ))}
          </div>
          <button
            onClick={() => setShowRules((v) => !v)}
            className="text-xs text-gray-400 hover:text-white uppercase tracking-wider transition-colors ml-4 shrink-0"
          >
            {showRules ? 'Hide Rules ▲' : 'Rules ▼'}
          </button>
        </div>

        {showRules && (
          <div className="border-t border-gray-700 pt-3 grid grid-cols-2 gap-x-8 gap-y-3 text-xs text-gray-300 w-full">
            <div>
              <p className="text-gray-400 uppercase tracking-wider mb-1">
                Objective
              </p>
              <p>
                Round all three course marks and cross the finish line first.
              </p>
            </div>
            <div>
              <p className="text-gray-400 uppercase tracking-wider mb-1">
                Movement
              </p>
              <p>
                Each turn consists of 1–3 legs determined by the die roll. Each
                leg is a straight line move.
              </p>
            </div>
            <div>
              <p className="text-gray-400 uppercase tracking-wider mb-1">
                Points of Sail
              </p>
              <ul className="space-y-0.5">
                <li>
                  Broad Reaching —{' '}
                  <span className="text-white font-medium">3 spaces</span>
                </li>
                <li>
                  Beam Reaching / Running —{' '}
                  <span className="text-white font-medium">2 spaces</span>
                </li>
                <li>
                  Beating —{' '}
                  <span className="text-white font-medium">1 space</span>
                </li>
                <li>
                  Luffing (into wind) —{' '}
                  <span className="text-white font-medium">0 spaces</span>
                </li>
              </ul>
            </div>
            <div>
              <p className="text-gray-400 uppercase tracking-wider mb-1">
                Basic Rules
              </p>
              <ul className="space-y-0.5">
                <li>Cannot move onto an occupied space.</li>
                <li>All legs must be completed each turn.</li>
                <li>No leg may be retraced within the same turn.</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
