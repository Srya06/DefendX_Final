export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Command Center</h1>
      <p className="text-gray-400 mb-8">Welcome to the DEFEND-X Defense Recruitment & Readiness Intelligence Platform.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-2">Recruitment Intelligence</h2>
          <p className="text-sm text-gray-400">Recruitment intelligence will be connected in Phase 4.</p>
        </div>

        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-2">Academic Preparation</h2>
          <p className="text-sm text-gray-400">Academic preparation will be connected in a later phase.</p>
        </div>

        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-2">Fitness Assessment</h2>
          <p className="text-sm text-gray-400 mb-4">Live camera fitness assessment will be connected in Phase 8.</p>
          <button disabled className="px-4 py-2 bg-gray-700 text-gray-500 rounded cursor-not-allowed text-sm font-medium">
            Start Live Fitness Assessment (Coming in Phase 8)
          </button>
        </div>

        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-2">Readiness</h2>
          <p className="text-sm text-gray-400">Defense Readiness Index will be calculated after candidate data becomes available.</p>
        </div>

        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 md:col-span-2">
          <h2 className="text-lg font-medium text-white mb-2">AI Mentor</h2>
          <p className="text-sm text-gray-400">Multi-agent intelligence will be connected in Phase 6.</p>
        </div>
      </div>
    </div>
  );
}
