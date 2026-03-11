import { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { GameResponse } from '../types/models';
import { LobbyPhase } from '../components/LobbyPhase';
import { Board } from '../components/Board';
import { SetupPhase } from '../components/SetupPhase';
import { RacingPhase } from '../components/RacingPhase';
import { FinishedPhase } from '../components/FinishedPhase';
import { authFetch } from '../utils/api';

export const GamePage = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const [loading, setLoading] = useState(true);
  const [game, setGame] = useState<GameResponse>();

  const errMsg = (gameId: string): string => {
    return `Failed to fetch game with gameId ${gameId}`;
  };

  const renderPhase = (playerId: string | null) => {
    if (!game) return null;
    if (game.phase === 'LOBBY')
      return (
        <>
          <Board board={game.board} yachts={game.yachts} />
          <LobbyPhase game={game} setGame={setGame} playerId={playerId} />
        </>
      );

    if (game.phase === 'SETUP')
      return <SetupPhase game={game} setGame={setGame} playerId={playerId} />;

    if (game.phase === 'RACING')
      return <RacingPhase game={game} setGame={setGame} playerId={playerId} />;

    if (game.phase === 'FINISHED')
      return (
        <FinishedPhase game={game} setGame={setGame} playerId={playerId} />
      );

    return null;
  };

  useEffect(() => {
    if (!gameId) return;

    setLoading(true);

    authFetch(`${import.meta.env.VITE_API_URL}/games/${gameId}`, {
      method: 'GET'
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(errMsg(gameId));
        }

        return response.json().then((gameResponse: GameResponse) => {
          setGame(gameResponse);
        });
      })
      .catch((error) => {
        console.error(errMsg(gameId), { error });
        throw error;
      })
      .finally(() => {
        setLoading(false);
      });
  }, [gameId]);

  useEffect(() => {
    if (!gameId) return;

    const webSocketUrl = import.meta.env.VITE_API_URL.replace(
      /^http:\/\//,
      'ws://'
    ).replace(/^https:\/\//, 'wss://');

    const token = localStorage.getItem('regatta_token');

    const webSocket = new WebSocket(
      `${webSocketUrl}/games/${gameId}/ws?token=${token}`
    );

    webSocket.onmessage = (event) => {
      const data: GameResponse = JSON.parse(event.data);
      setGame(data);
    };

    return () => {
      webSocket.close();
    };
  }, [gameId]);

  if (!gameId) return null;

  const playerId = localStorage.getItem(`regatta_player_${gameId}`) ?? null;

  return (
    <div className="min-h-screen flex flex-col items-center py-8 px-4">
      <div className="flex flex-col items-center w-fit min-w-80">
        <h1 className="text-center text-3xl font-bold tracking-[1em] text-white mb-6">
          REGATTA
        </h1>

        {loading ? (
          <span className="text-gray-400 tracking-widest">LOADING...</span>
        ) : (
          renderPhase(playerId)
        )}
      </div>
    </div>
  );
};
