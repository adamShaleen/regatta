import { Routes, Route } from 'react-router';
import { LobbyPage } from './pages/LobbyPage';
import { GamePage } from './pages/GamePage';

export default function App() {
  return (
    <div>
      <h1>Regatta</h1>
      <p>A Turn-based Sailboat racing game</p>
      <Routes>
        <Route path="/" element={<LobbyPage />} />
        <Route path="/game/:gameId" element={<GamePage />} />
      </Routes>
    </div>
  );
}
