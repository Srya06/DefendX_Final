'use client';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();

  if (loading) {
    return <div className="flex h-screen items-center justify-center bg-gray-900 text-white">Loading DEFEND-X...</div>;
  }

  if (!user) {
    return null; // Will redirect in AuthContext
  }

  const navItems = [
    { name: 'Overview', path: '/dashboard', active: pathname === '/dashboard' },
    { name: 'Profile', path: '/profile', active: pathname === '/profile' },
    { name: 'Recruitment Intelligence', path: '/recruitment', active: pathname === '/recruitment' },
    { name: 'Academic Preparation', path: '#', active: false, disabled: true },
    { name: 'Fitness Assessment', path: '#', active: false, disabled: true },
    { name: 'Readiness', path: '#', active: false, disabled: true },
    { name: 'AI Mentor', path: '#', active: false, disabled: true },
    { name: 'Account Settings', path: '/account', active: pathname === '/account' },
  ];

  return (
    <div className="flex h-screen bg-gray-900 text-white flex-col md:flex-row">
      {/* Sidebar Desktop */}
      <aside className="w-full md:w-64 bg-gray-800 border-r border-gray-700 flex flex-col hidden md:flex">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold tracking-wider text-blue-400">DEFEND-X</h1>
          <p className="text-xs text-gray-400 mt-1 uppercase">Intelligence Platform</p>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-2">
          {navItems.map((item, idx) => (
            <div key={idx}>
              {item.disabled ? (
                <div className="px-4 py-2 text-sm text-gray-500 cursor-not-allowed flex items-center justify-between">
                  {item.name}
                </div>
              ) : (
                <Link
                  href={item.path}
                  className={`block px-4 py-2 text-sm rounded transition-colors ${
                    item.active ? 'bg-blue-600 text-white font-medium' : 'text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {item.name}
                </Link>
              )}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6 md:px-8">
          <div className="md:hidden font-bold text-blue-400">DEFEND-X</div>
          <div className="flex items-center space-x-4 ml-auto">
            <span className="text-sm text-gray-300">ID: <span className="font-mono text-gray-100">{user.user_id}</span></span>
            <button
              onClick={logout}
              className="text-sm px-3 py-1 bg-gray-700 hover:bg-red-600 rounded transition-colors"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Mobile Nav (simple bottom or inline for this phase) */}
        <nav className="md:hidden bg-gray-800 border-b border-gray-700 flex overflow-x-auto whitespace-nowrap scrollbar-hide">
          {navItems.filter(i => !i.disabled).map((item, idx) => (
             <Link
               key={idx}
               href={item.path}
               className={`px-4 py-3 text-sm transition-colors ${
                 item.active ? 'border-b-2 border-blue-500 text-blue-400 font-medium' : 'text-gray-400'
               }`}
             >
               {item.name}
             </Link>
          ))}
        </nav>

        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-4xl mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
