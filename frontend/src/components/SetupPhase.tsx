import { PhaseProps } from '../types/models';
import { InteractiveBoard } from './InteractiveBoard';

export const SetupPhase = ({ game, setGame }: PhaseProps) => {
  const handleCellClick = async (x: number, y: number) => {
    const playerId = game.setup_order[game.current_player_index];

    const response = await fetch(
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
    <InteractiveBoard
      board={game.board}
      yachts={game.yachts}
      onCellClick={handleCellClick}
    />
  );
};
