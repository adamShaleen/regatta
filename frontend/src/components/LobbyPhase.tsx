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
      setPlayerId('');
      localStorage.setItem(`regatta_player_${game.id}`, playerId);
    } catch (error) {
      console.error(errMsg(game.id, 'add player'));
      throw error;
    }
  };

  const handleStartSetup = async (): Promise<void> => {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/games/${game.id}/start`,
        { method: 'POST' }
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

  const maxPlayersReached = game.players.length >= 6;

  return (
    <div className="mt-6 bg-[#1e2d3d] rounded-xl p-6 w-full max-w-md flex flex-col gap-4">
      <div className="flex gap-2">
        <input
          disabled={maxPlayersReached}
          className="flex-1 bg-[#0f1923] text-white border border-gray-600 rounded-lg px-4 py-2 placeholder-gray-500 focus:outline-none focus:border-yellow-400 disabled:opacity-40 disabled:cursor-not-allowed"
          placeholder={
            maxPlayersReached ? 'Max players reached' : 'Enter player name'
          }
          value={playerId}
          onChange={(e) => setPlayerId(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddPlayer()}
        />
        <button
          disabled={maxPlayersReached}
          onClick={handleAddPlayer}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold px-4 py-2 rounded-lg tracking-wider transition-colors"
        >
          ADD
        </button>
      </div>

      {game.players.length > 0 && (
        <div>
          <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-2">
            Players
          </h3>
          <div className="flex flex-wrap gap-2">
            {game.players.map((player) => (
              <span
                key={player}
                className="bg-[#0f1923] text-white px-3 py-1 rounded-full text-sm"
              >
                {player}
              </span>
            ))}
          </div>
        </div>
      )}

      <button
        disabled={game.players.length < 2}
        onClick={handleStartSetup}
        className="bg-yellow-400 hover:bg-yellow-300 disabled:bg-gray-700 disabled:text-gray-500 text-gray-900 font-bold py-2 rounded-lg tracking-wider transition-colors"
      >
        START GAME
      </button>
    </div>
  );
};
