'use client';
import { useState } from 'react';

export default function RetrievalTestPage() {
  const [query, setQuery] = useState('');
  const [force, setForce] = useState('Indian Navy');
  const [results, setResults] = useState<any[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleRetrieve = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResults([]);
    setStatus(null);
    try {
      const res = await fetch('http://localhost:8000/api/v1/rag/retrieve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query, force, top_k: 5 }),
      });
      const data = await res.json();
      setResults(data.results || []);
      setStatus(data.grounding_status);
    } catch (err) {
      console.error(err);
      setStatus("ERROR");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white mb-6">Developer: RAG Retrieval Test</h1>
      
      <form onSubmit={handleRetrieve} className="bg-gray-800 p-6 rounded-lg space-y-4">
        <div>
          <label className="block text-gray-300 font-medium mb-1">Query</label>
          <input 
            type="text"
            className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white"
            placeholder="e.g. Navy SSR physical standards"
            value={query}
            onChange={e => setQuery(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-gray-300 font-medium mb-1">Force Constraint</label>
          <select
            className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white"
            value={force}
            onChange={e => setForce(e.target.value)}
          >
            <option value="Indian Navy">Indian Navy</option>
            <option value="Indian Army">Indian Army</option>
            <option value="Indian Air Force">Indian Air Force</option>
            <option value="Police">Police</option>
          </select>
        </div>
        <button 
          type="submit" 
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors"
        >
          {loading ? 'Retrieving...' : 'Retrieve Evidence'}
        </button>
      </form>

      {status && (
        <div className={`p-4 rounded-lg font-bold border ${status === 'GROUNDED' ? 'bg-green-900/30 border-green-500 text-green-400' : 'bg-red-900/30 border-red-500 text-red-400'}`}>
          Status: {status}
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4 mt-6">
          <h2 className="text-xl font-bold text-gray-200">Results</h2>
          {results.map((r, i) => (
            <div key={r.evidence_id || i} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">Score: {r.score?.toFixed(2)}</span>
                <span className="text-xs bg-purple-900 text-purple-300 px-2 py-1 rounded">{r.retrieval_source}</span>
              </div>
              <p className="text-gray-300 mb-3">{r.text}</p>
              <div className="text-xs text-gray-500 space-y-1">
                <div>Document ID: {r.document_id || 'N/A'}</div>
                <div>Page: {r.page_start || 'N/A'}</div>
                <div>Extraction: {r.extraction_method || 'N/A'}</div>
                {r.source_url && (
                  <a href={r.source_url} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline">View Source</a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
