'use client';
import { useState } from 'react';
import Head from 'next/head';

interface Evidence {
  document_id: string;
  page_start: number;
  source_url: string;
  text: string;
}

interface AgentTrace {
  agent: string;
  status: string;
  tools_used?: string[];
  note?: string;
}

interface AgentResponse {
  request_id: string;
  response: string;
  selected_agents: string[];
  evidence: Evidence[];
  execution_trace: AgentTrace[];
  warnings: string[];
}

export default function MentorPage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch('http://localhost:8000/api/v1/agents/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, target_force: 'Indian Navy' }) // Example hardcode force context
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || 'Failed to fetch mentor response');
      }

      const data: AgentResponse = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col p-4 md:p-8">
      <Head>
        <title>DEFEND-X | AI Mentor</title>
      </Head>

      <main className="max-w-4xl w-full mx-auto bg-white shadow rounded-lg overflow-hidden flex flex-col">
        <div className="bg-blue-900 text-white p-6">
          <h1 className="text-2xl font-bold">DEFEND-X AI Mentor</h1>
          <p className="text-blue-200 mt-1">Multi-Agent Intelligence powered by Local Ollama</p>
        </div>

        <div className="p-6 flex flex-col space-y-6">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              className="flex-1 border rounded p-3 text-gray-800"
              placeholder="Ask about Navy physical standards, academic prep, etc..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded font-medium disabled:opacity-50"
            >
              {loading ? 'Thinking...' : 'Ask Mentor'}
            </button>
          </form>

          {error && (
            <div className="bg-red-50 text-red-700 p-4 rounded border border-red-200">
              <h3 className="font-bold">Error</h3>
              <p>{error}</p>
            </div>
          )}

          {result && (
            <div className="flex flex-col space-y-6 animate-fade-in">
              <div className="bg-blue-50 border border-blue-100 p-6 rounded text-gray-800 text-lg whitespace-pre-wrap">
                {result.response}
              </div>

              {result.warnings?.length > 0 && (
                <div className="bg-yellow-50 text-yellow-800 p-4 rounded border border-yellow-200">
                  <h4 className="font-bold mb-2">Warnings</h4>
                  <ul className="list-disc pl-5">
                    {result.warnings.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Agent Execution Trace</h3>
                  <div className="bg-gray-50 rounded border p-4 space-y-3">
                    {result.execution_trace.map((trace, i) => (
                      <div key={i} className="flex items-start">
                        <span className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded mr-2 mt-0.5">
                          {trace.agent}
                        </span>
                        <div>
                          <p className="text-sm font-medium">{trace.status}</p>
                          {trace.tools_used && (
                            <p className="text-xs text-gray-500">Tools: {trace.tools_used.join(', ')}</p>
                          )}
                          {trace.note && (
                            <p className="text-xs text-amber-600">{trace.note}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Retrieved Evidence</h3>
                  {result.evidence.length === 0 ? (
                    <p className="text-sm text-gray-500 italic">No direct recruitment evidence retrieved.</p>
                  ) : (
                    <div className="space-y-3">
                      {result.evidence.map((ev, i) => (
                        <div key={i} className="text-sm border-l-2 border-blue-400 pl-3 py-1">
                          <p className="text-gray-700 mb-1">"{ev.text}"</p>
                          <a href={ev.source_url} target="_blank" rel="noreferrer" className="text-xs text-blue-600 hover:underline">
                            Source Document (Page {ev.page_start || 'N/A'})
                          </a>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
