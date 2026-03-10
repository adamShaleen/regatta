import { useState } from 'react';
import { useNavigate } from 'react-router';

export const LobbyPage = () => {
  const navigate = useNavigate();
  const [gameId, setGameId] = useState<string>('');

  const handleCreateGame = async (): Promise<void> => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/games/`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to create game: ${response.status}`);
      }

      const { id } = await response.json();
      navigate(`/game/${id}`);
    } catch (error) {
      console.error('There was an error calling handleCreateGame', {
        error
      });

      throw error;
    }
  };

  const handleJoinGame = (): void => {
    navigate(`/game/${gameId}`);
  };

  return (
    <div>
      <section>
        <button onClick={handleCreateGame}>CREATE GAME</button>
      </section>

      <section>
        <input
          placeholder="INSERT GAME ID"
          onChange={(e) => setGameId(e.target.value)}
        />
        <button onClick={handleJoinGame}>JOIN GAME</button>
      </section>
    </div>
  );
};
