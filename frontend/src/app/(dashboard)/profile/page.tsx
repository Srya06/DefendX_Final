'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

export default function ProfilePage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [fullName, setFullName] = useState('');
  const [targetForce, setTargetForce] = useState('');
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/profile', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setFullName(data.full_name || '');
        setTargetForce(data.target_force || '');
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load profile' });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const res = await fetch('http://localhost:8000/api/v1/profile', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: fullName,
          target_force: targetForce || null,
        }),
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to update profile');
      setMessage({ type: 'success', text: 'Profile updated successfully' });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading profile...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-white">Profile</h1>
      
      {message && (
        <div className={`p-4 rounded ${message.type === 'success' ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleUpdate} className="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4 max-w-xl">
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-300">Full Name</label>
          <input
            id="full_name"
            type="text"
            className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>

        <div>
          <label htmlFor="target_force" className="block text-sm font-medium text-gray-300">Target Force</label>
          <select
            id="target_force"
            className="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={targetForce}
            onChange={(e) => setTargetForce(e.target.value)}
          >
            <option value="">Select a force...</option>
            <option value="Indian Army">Indian Army</option>
            <option value="Indian Navy">Indian Navy</option>
            <option value="Indian Air Force">Indian Air Force</option>
            <option value="Police">Police</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 font-medium"
        >
          {saving ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  );
}
