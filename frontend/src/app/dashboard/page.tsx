import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold">Research Workspaces</h1>
        <Linkh href="/" className="text-sm text-slate-400 hover:text-white">
          ↁ Back to Home
        </Link>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-slate-800 rounded-lg border border-slate-700">
          <h2 className="text-xl font-semibold mb-2">Compliance AI Literature Review</h2>
          <p className="text-slate-400 text-smmb-4">
            Mode: Academic | Status: Completed
          </p>
          <div className="text-xs bg-slate-900 p-2 rounded text-slate-300">
            Last updated: 2 days ago
          </div>
        </div>
        <div className="p-6 bg-slate-800/50 rounded-lg border border-dashed border-slate-700 flex items-center justify-center">
          <p className="text-slate-500">+ Create New Workspace (Milestone 1.3)</p>
        </div>
      </div>
    </div>
  );
}
