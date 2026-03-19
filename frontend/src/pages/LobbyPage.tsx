import { useState } from 'react';
import { useNavigate } from 'react-router';
import { authFetch } from '../utils/api';
import { LoadingButton } from '../components/LoadingButton';

export const LobbyPage = () => {
  const navigate = useNavigate();
  const [gameId, setGameId] = useState<string>('');

  const handleCreateGame = async (): Promise<void> => {
    try {
      const response = await authFetch(
        `${import.meta.env.VITE_API_URL}/games/`,
        {
          method: 'POST'
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to create game: ${response.status}`);
      }

      const { id } = await response.json();
      navigate(`/game/${id}`);
    } catch (error) {
      console.error('There was an error calling handleCreateGame', { error });
      throw error;
    }
  };

  const handleJoinGame = (): void => {
    navigate(`/game/${gameId}`);
  };

  return (
    <div className="min-h-screen flex flex-col items-center py-8 px-4">
      <div className="flex flex-col items-center w-full max-w-sm">
        <h1 className="w-full text-center text-3xl font-bold tracking-[1em] text-white mb-6">
          REGATTA
        </h1>

        <div className="flex flex-col gap-4 w-full">
          <LoadingButton
            buttonText="CREATE GAME"
            buttonClickFunction={handleCreateGame}
            styles="bg-yellow-400 hover:bg-yellow-300 text-gray-900 py-3"
          />

          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-gray-600" />
            <span className="text-gray-500 text-sm tracking-wider">or</span>
            <div className="flex-1 h-px bg-gray-600" />
          </div>

          <div className="flex flex-col gap-2">
            <input
              className="bg-[#1e2d3d] text-white border border-gray-600 px-4 py-2 placeholder-gray-500 focus:outline-none focus:border-yellow-400"
              placeholder="Enter game ID"
              onChange={(e) => setGameId(e.target.value)}
            />
            <button
              onClick={handleJoinGame}
              className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 tracking-wider transition-colors"
            >
              JOIN GAME
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
