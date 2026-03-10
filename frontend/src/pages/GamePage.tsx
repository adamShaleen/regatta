import { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { GameResponse } from '../types/models';
import { LobbyPhase } from '../components/LobbyPhase';
import { Board } from '../components/Board';
import { SetupPhase } from '../components/SetupPhase';
import { RacingPhase } from '../components/RacingPhase';

export const GamePage = () => {
  const { gameId } = useParams<{ gameId: string }>();
  const [loading, setLoading] = useState(true);
  const [game, setGame] = useState<GameResponse>();

  const errMsg = (gameId: string): string => {
    return `Failed to fetch game with gameId ${gameId}`;
  };

  const renderPhase = () => {
    if (!game) return null;
    if (game.phase === 'LOBBY')
      return (
        <>
          <Board board={game.board} yachts={game.yachts} />
          <LobbyPhase game={game} setGame={setGame} />
        </>
      );

    if (game.phase === 'SETUP')
      return <SetupPhase game={game} setGame={setGame} />;

    if (game.phase === 'RACING')
      return <RacingPhase game={game} setGame={setGame} />;

    return null;
  };

  useEffect(() => {
    if (!gameId) return;

    setLoading(true);

    fetch(`${import.meta.env.VITE_API_URL}/games/${gameId}`, { method: 'GET' })
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

  if (!gameId) return null;

  return (
    <div>
      <h3>GAME PAGE</h3>

      <section>
        {loading ? <span>...LOADING</span> : <>{renderPhase()}</>}
      </section>
    </div>
  );
};
