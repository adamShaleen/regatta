import { PhaseProps } from '../types/models';
import { YACHT_COLORS } from './Board';
import { InteractiveBoard } from './InteractiveBoard';

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

const WIND_DIRECTION_LABELS: Record<number, string> = {
  0: 'N',
  45: 'NE',
  90: 'E',
  135: 'SE',
  180: 'S',
  225: 'SW',
  270: 'W',
  315: 'NW'
};

export const RacingPhase = ({ game, setGame }: PhaseProps) => {
  const currentPlayer = game.setup_order[game.current_player_index];
  const currentPlayerPosition = game.yachts[currentPlayer];
  const colorIndex = Object.keys(game.yachts).indexOf(currentPlayer);
  console.log('current player position:', currentPlayerPosition.position);

  const startRound = async () => {
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/games/${game.id}/round`,
      { method: 'POST' }
    );

    if (!response.ok) {
      const errMsg = `There was an error setting starting the round for gameId ${game.id}`;

      console.error(errMsg);
      throw new Error(errMsg);
    }

    setGame(await response.json());
  };

  const handleCellClick = async (x: number, y: number) => {
    const dx = x - currentPlayerPosition.position.x;
    const dy = y - currentPlayerPosition.position.y;

    const heading = HEADING_MAP[`${dx},${dy}`];
    console.log(dx, dy, heading);
    if (heading === undefined) return;

    const response = await fetch(
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
      const errMsg = `There was an error setting selecting position for player ${game.setup_order[game.current_player_index]}`;

      console.error(errMsg);
      throw new Error(errMsg);
    }

    setGame(await response.json());
  };

  return (
    <>
      <button onClick={startRound}>START ROUND</button>
      <p style={{ color: YACHT_COLORS[colorIndex] }}>
        Current Player: {game.setup_order[game.current_player_index]}
      </p>

      <p>Wind Direction: {WIND_DIRECTION_LABELS[game.wind_direction]}</p>

      <InteractiveBoard
        board={game.board}
        yachts={game.yachts}
        onCellClick={handleCellClick}
      />
    </>
  );
};
