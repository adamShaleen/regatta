export const authFetch = async (url: string, options?: RequestInit) => {
  const token = localStorage.getItem('regatta_token');

  const response = await fetch(url, {
    ...options,
    headers: { ...options?.headers, Authorization: `Bearer ${token}` }
  });

  if (response.status === 401) {
    localStorage.removeItem('regatta_token');
    window.location.href = '/login';
  }

  return response;
};
