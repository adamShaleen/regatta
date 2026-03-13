import { Routes, Route, Navigate, useLocation } from 'react-router';
import { LobbyPage } from './pages/LobbyPage';
import { GamePage } from './pages/GamePage';
import { LoginPage } from './pages/LoginPage';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('regatta_token');
  const location = useLocation();

  if (!token)
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;

  return children;
};

export default function App() {
  return (
    <div>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <LobbyPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/game/:gameId"
          element={
            <ProtectedRoute>
              <GamePage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}
