import { useState } from 'react';
import { PhaseProps } from '../types/models';

export const LobbyPhase = ({ game, setGame }: PhaseProps) => {
  const [playerId, setPlayerId] = useState('');

  const errMsg = (gameId: string, operation: string): string => {
    return `Failed to ${operation} to game with gameId ${gameId}`;
  };

  const handleAddPlayer = async (): Promise<void> => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/games/${game.id}/players`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ player_id: playerId })
        }
      );

      if (!response.ok) {
        console.error(errMsg(game.id, 'add player'));
        throw new Error(errMsg(game.id, 'add player'));
      }

      setGame(await response.json());
    } catch (error) {
      console.error(errMsg(game.id, 'add player'));
      throw error;
    }
  };

  const handleStartSetup = async (): Promise<void> => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/games/${game.id}/start`,
        {
          method: 'POST'
        }
      );

      if (!response.ok) {
        console.error(errMsg(game.id, 'start setup'));
        throw new Error(errMsg(game.id, 'start setup'));
      }

      setGame(await response.json());
    } catch (error) {
      console.error(errMsg(game.id, 'start setup'));
      throw error;
    }
  };

  return (
    <div>
      <section>
        <input
          placeholder="INSERT PLAYER ID"
          onChange={(e) => setPlayerId(e.target.value)}
        />
        <button onClick={handleAddPlayer}>ADD PLAYER</button>
        <button disabled={game.players.length < 2} onClick={handleStartSetup}>
          START GAME
        </button>
      </section>

      <section>
        <h3>PLAYERS IN GAME</h3>
        {game.players.map((player) => {
          return <span key={player}>{player}</span>;
        })}
      </section>
    </div>
  );
};
