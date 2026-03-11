import { useNavigate } from 'react-router';
import { PhaseProps } from '../types/models';

export const FinishedPhase = ({ game }: PhaseProps) => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center gap-6 mt-8">
      <div className="text-yellow-400 text-4xl font-bold tracking-widest">
        WINNER
      </div>
      <div className="text-white text-2xl font-bold">{game.winner}</div>
      <div>
        <button
          onClick={() => navigate('/')}
          className="bg-yellow-400 hover:bg-yellow-300 text-gray-900 font-bold px-6 py-2 rounded-lg tracking-wider transition-colors"
        >
          NEW GAME
        </button>
      </div>
    </div>
  );
};
