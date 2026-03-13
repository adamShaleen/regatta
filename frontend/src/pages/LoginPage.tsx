import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router';

export const LoginPage = () => {
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');

  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string })?.from ?? '/';

  const handleLogin = async (): Promise<void> => {
    setError('');

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/auth/login`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password })
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to login: ${response.status}`);
      }

      const data = await response.json();

      localStorage.setItem('regatta_token', data.access_token);
      navigate(from, { replace: true });
    } catch (error) {
      console.error('There was an error calling handleLogin', { error });
      setError('Invalid password');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center py-8 px-4">
      <div className="flex flex-col items-center w-full max-w-sm">
        <h1 className="w-full text-center text-3xl font-bold tracking-[1em] text-white mb-6">
          REGATTA
        </h1>

        <div className="flex flex-col gap-2 w-full">
          <input
            type="password"
            className="bg-[#1e2d3d] text-white border border-gray-600 px-4 py-2 placeholder-gray-500 focus:outline-none focus:border-yellow-400"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
          />
          <button
            onClick={handleLogin}
            className="bg-yellow-400 hover:bg-yellow-300 text-gray-900 font-bold py-3 tracking-wider transition-colors"
          >
            LOGIN
          </button>
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        </div>
      </div>
    </div>
  );
};
