'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';

type Force = { id: string; name: string };
type Notification = { id: string; category_id: string; title: string; status: string };
type Detail = Notification & {
  eligibility_requirements: any[];
  physical_standards: any[];
  medical_standards: any[];
  important_dates: any[];
  selection_stages: any[];
  vacancies: any[];
};

export default function RecruitmentPage() {
  const { user } = useAuth();
  const [forces, setForces] = useState<Force[]>([]);
  const [selectedForce, setSelectedForce] = useState<string>('');
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [selectedNotifId, setSelectedNotifId] = useState<string | null>(null);
  const [details, setDetails] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(true);

  // 1. Load available forces & set default from user profile if available
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/recruitment/forces', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setForces(data);
        // We need the user's actual target force from /profile to default here.
        // For now, if the auth context holds the actual target_force (which we didn't add to context yet), 
        // we could use it. Let's fetch profile to get target force.
        fetch('http://localhost:8000/api/v1/profile', { credentials: 'include' })
          .then(r => r.json())
          .then(prof => {
            if (prof.target_force && data.some((f: Force) => f.name === prof.target_force)) {
              setSelectedForce(prof.target_force);
            } else if (data.length > 0) {
              setSelectedForce(data[0].name);
            }
          });
      })
      .finally(() => setLoading(false));
  }, []);

  // 2. Load notifications when force changes
  useEffect(() => {
    if (!selectedForce) return;
    setDetails(null);
    setSelectedNotifId(null);
    fetch(`http://localhost:8000/api/v1/recruitment/notifications?target_force=${encodeURIComponent(selectedForce)}`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setNotifications(data || []));
  }, [selectedForce]);

  // 3. Load details when a notification is selected
  useEffect(() => {
    if (!selectedNotifId) return;
    fetch(`http://localhost:8000/api/v1/recruitment/notifications/${selectedNotifId}`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setDetails(data));
  }, [selectedNotifId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-white mb-6">Recruitment Intelligence</h1>
      
      <div className="flex items-center space-x-4 mb-6">
        <label className="text-gray-300 font-medium">Target Force Filter:</label>
        <select 
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
          value={selectedForce}
          onChange={e => setSelectedForce(e.target.value)}
        >
          {forces.map(f => (
            <option key={f.id} value={f.name}>{f.name}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* List Column */}
        <div className="md:col-span-1 space-y-4">
          <h2 className="text-xl font-semibold text-gray-200">Active Notifications</h2>
          {notifications.length === 0 ? (
            <p className="text-gray-400 italic">No notifications found for this force.</p>
          ) : (
            notifications.map(n => (
              <button
                key={n.id}
                onClick={() => setSelectedNotifId(n.id)}
                className={`w-full text-left p-4 rounded-lg border ${
                  selectedNotifId === n.id ? 'bg-blue-900 border-blue-500' : 'bg-gray-800 border-gray-700 hover:bg-gray-750'
                }`}
              >
                <div className="font-medium">{n.title}</div>
                <div className="text-xs text-gray-400 mt-1 uppercase">{n.status}</div>
              </button>
            ))
          )}
        </div>

        {/* Details Column */}
        <div className="md:col-span-2">
          {details ? (
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-6">
              <h2 className="text-2xl font-bold">{details.title}</h2>
              
              <div className="space-y-4">
                <Section title="Eligibility" items={details.eligibility_requirements} />
                <Section title="Physical Standards" items={details.physical_standards} />
                <Section title="Medical Standards" items={details.medical_standards} />
              </div>
            </div>
          ) : (
            <div className="flex h-full items-center justify-center border-2 border-dashed border-gray-700 rounded-lg p-12 text-gray-500">
              Select a notification to view intelligence
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Section({ title, items }: { title: string, items: any[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h3 className="text-lg font-semibold text-blue-400 mb-2">{title}</h3>
      <div className="space-y-3">
        {items.map(item => (
          <div key={item.id} className="bg-gray-900 rounded p-4 border border-gray-750">
            <p className="text-gray-200">{item.text_content}</p>
            {item.source_url && (
              <div className="mt-3 pt-3 border-t border-gray-800 text-xs text-gray-400 flex flex-col space-y-1">
                <span className="font-semibold text-gray-300">Official Source</span>
                {item.document_id && <span>Document ID: {item.document_id}</span>}
                {item.page_start && <span>Page: {item.page_start}</span>}
                <a href={item.source_url} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">
                  [View Source]
                </a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
