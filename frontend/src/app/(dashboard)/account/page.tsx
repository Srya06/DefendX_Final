'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

export default function AccountPage() {
  const { user, refreshAuth } = useAuth();
  const [newUserId, setNewUserId] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleUpdateUserId = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

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
      
      setMessage('User ID updated successfully');
      setNewUserId('');
      await refreshAuth();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-white mb-8">Account Settings</h1>
      
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700 mb-8 max-w-xl">
        <h2 className="text-xl font-semibold mb-4">Current Profile</h2>
        <div className="grid grid-cols-2 gap-4 text-gray-300">
          <div>
            <span className="font-medium text-gray-400">User ID:</span> {user?.user_id}
          </div>
          <div>
            <span className="font-medium text-gray-400">Role:</span> {user?.role}
          </div>
          <div>
            <span className="font-medium text-gray-400">Status:</span> ACTIVE
          </div>
        </div>
      </div>
      
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-700 max-w-xl">
        <h2 className="text-xl font-semibold mb-4">Change User ID</h2>
        {error && <div className="bg-red-900 text-red-200 p-3 rounded mb-4 text-sm">{error}</div>}
        {message && <div className="bg-green-900 text-green-200 p-3 rounded mb-4 text-sm">{message}</div>}
        
        <form onSubmit={handleUpdateUserId} className="flex gap-4 items-end">
          <div className="flex-1">
            <label htmlFor="acc-new-userid" className="block text-sm font-medium text-gray-300">New User ID</label>
            <input
              id="acc-new-userid"
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
  );
}
