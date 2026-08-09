"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import WorkspaceModal from "@/components/workspace/WorkspaceModal";

interface Workspace {
  id: string;
  title: string;
  description?: string;
  research_mode: "Quick" | "Deep" | "Academic";
  status: string;
  created_at: string;
  updated_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const fetchWorkspaces = async (authToken: string) => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/workspaces", {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (!res.ok) {
        throw new Error("Failed to load workspaces");
      }

      const data = await res.json();
      setWorkspaces(data);
    } catch (err: any) {
      setError(err.message || "Error fetching workspaces");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (!storedToken) {
      router.push("/login");
      return;
    }
    setToken(storedToken);
    fetchWorkspaces(storedToken);
  }, [router]);

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold">Research Workspaces</h1>
          <p className="text-sm text-slate-400">Manage and orchestrate deep research sessions</p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsModalOpen(true)}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500 transition-colors shadow-lg shadow-indigo-500/20"
          >
            + Create Workspace
          </button>
          <Link href="/" className="text-sm text-slate-400 hover:text-white">
            Home
          </Link>
        </div>
      </header>

      {error && (
        <div className="mb-6 rounded bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 rounded-lg bg-slate-800/50 animate-pulse border border-slate-800" />
          ))}
        </div>
      ) : workspaces.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-800 p-12 text-center bg-slate-800/20">
          <h3 className="text-lg font-semibold text-slate-300 mb-2">No Workspaces Found</h3>
          <p className="text-sm text-slate-500 mb-6">
            Get started by creating your first deep research workspace.
          </p>
          <button
            onClick={() => setIsModalOpen(true)}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500"
          >
            + Create Workspace
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {workspaces.map((ws) => (
            <Link
              key={ws.id}
              href={`/workspace/${ws.id}`}
              className="group p-6 bg-slate-800 hover:bg-slate-800/80 rounded-xl border border-slate-700 hover:border-indigo-500/50 transition-all duration-200 shadow-md flex flex-col justify-between"
            >
              <div>
                <div className="flex justify-between items-start mb-2">
                  <h2 className="text-lg font-bold group-hover:text-indigo-400 transition-colors line-clamp-1">
                    {ws.title}
                  </h2>
                  <span className="text-xs px-2.5 py-1 rounded-full bg-slate-700 font-medium text-slate-300 border border-slate-600">
                    {ws.research_mode}
                  </span>
                </div>
                <p className="text-slate-400 text-sm mb-4 line-clamp-2">
                  {ws.description || "No description provided."}
                </p>
              </div>
              <div className="text-xs text-slate-500 flex justify-between items-center pt-4 border-t border-slate-700/50">
                <span>Status: <strong className="text-emerald-400">{ws.status}</strong></span>
                <span>Created {new Date(ws.created_at).toLocaleDateString()}</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {token && (
        <WorkspaceModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onCreated={() => fetchWorkspaces(token)}
          token={token}
        />
      )}
    </div>
  );
}
