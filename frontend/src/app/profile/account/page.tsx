'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function AccountPage() {
  const [userId, setUserId] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [newUserId, setNewUserId] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/auth/me', {
          credentials: 'include',
        });
        if (!res.ok) {
          throw new Error('Not authenticated');
        }
        const data = await res.json();
        if (data.must_change_password) {
          router.push('/change-password');
          return;
        }
        setUserId(data.user_id);
        setRole(data.role);
      } catch (err) {
        router.push('/login');
      }
    };
    fetchUser();
  }, [router]);

  const handleUpdateUserId = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    setError('');
    try {
      const res = await fetch('http://localhost:8000/api/v1/profile/username', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_username: newUserId }),
        credentials: 'include',
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Update failed');
      }
      const data = await res.json();
      setUserId(data.new_username);
      setMessage('User ID updated successfully');
      setNewUserId('');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:8000/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
      router.push('/login');
    } catch (err) {
      console.error(err);
    }
  };

  if (!userId) return <div className="p-24 text-white">Loading...</div>;

  return (
    <div className="min-h-screen p-8 bg-gray-900 text-white">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
          <h1 className="text-3xl font-bold text-blue-400">Account Settings</h1>
          <button onClick={handleLogout} className="px-4 py-2 bg-red-600 rounded hover:bg-red-700">Logout</button>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
          <h2 className="text-xl font-semibold mb-4">Current Profile</h2>
          <div className="grid grid-cols-2 gap-4 text-gray-300">
            <div><span className="font-medium text-gray-400">User ID:</span> {userId}</div>
            <div><span className="font-medium text-gray-400">Role:</span> {role}</div>
            <div><span className="font-medium text-gray-400">Status:</span> ACTIVE</div>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Change User ID</h2>
          {message && <div className="bg-green-900 text-green-200 p-3 rounded mb-4">{message}</div>}
          {error && <div className="bg-red-900 text-red-200 p-3 rounded mb-4">{error}</div>}
          
          <form onSubmit={handleUpdateUserId} className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300">New User ID</label>
              <input
                type="text"
                className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={newUserId}
                onChange={e => setNewUserId(e.target.value)}
                required
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Update ID
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
