"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import DocumentUpload from "@/components/workspace/DocumentUpload";

interface Workspace {
  id: string;
  title: string;
  description?: string;
  research_mode: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface Document {
  id: string;
  workspace_id: string;
  filename: string;
  mime_type: string;
  file_size: number;
  created_at: string;
}

type TabType = "Overview" | "Plan" | "Documents" | "Evidence" | "Timeline" | "Report" | "Metrics";

export default function WorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const workspaceId = params.id as string;

  const [activeTab, setActiveTab] = useState<TabType>("Overview");
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const fetchWorkspace = useCallback(async (authToken: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/workspaces/${workspaceId}`, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (!res.ok) throw new Error("Workspace not found or unauthorized");
      const data = await res.json();
      setWorkspace(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  const fetchDocuments = useCallback(async (authToken: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/workspaces/${workspaceId}/documents`, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (_) {}
  }, [workspaceId]);

  const handleDeleteDocument = async (docId: string) => {
    if (!token) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/workspaces/${workspaceId}/documents/${docId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        fetchDocuments(token);
      }
    } catch (_) {}
  };

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (!storedToken) {
      router.push("/login");
      return;
    }
    setToken(storedToken);
    fetchWorkspace(storedToken);
    fetchDocuments(storedToken);
  }, [workspaceId, router, fetchWorkspace, fetchDocuments]);


  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white p-8">
        <div className="h-8 w-64 bg-slate-800 animate-pulse rounded mb-4" />
        <div className="h-4 w-96 bg-slate-800 animate-pulse rounded mb-8" />
        <div className="h-96 w-full bg-slate-800/50 animate-pulse rounded-xl" />
      </div>
    );
  }

  if (error || !workspace) {
    return (
      <div className="min-h-screen bg-slate-900 text-white p-8 flex flex-col items-center justify-center">
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-8 text-center max-w-md">
          <h2 className="text-xl font-bold text-red-400 mb-2">Error Loading Workspace</h2>
          <p className="text-sm text-slate-400 mb-6">{error || "Workspace not found"}</p>
          <Link href="/dashboard" className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const tabs: TabType[] = ["Overview", "Plan", "Documents", "Evidence", "Timeline", "Report", "Metrics"];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Workspace Header */}
      <header className="border-b border-slate-800 bg-slate-950 px-8 py-4">
        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center space-x-3">
            <Link href="/dashboard" className="text-sm text-slate-400 hover:text-white transition-colors">
              ← Dashboard
            </Link>
            <span className="text-slate-600">/</span>
            <h1 className="text-xl font-bold text-white">{workspace.title}</h1>
            <span className="rounded-full bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 text-xs font-semibold text-indigo-400">
              {workspace.research_mode}
            </span>
          </div>
          <div className="text-xs text-slate-400">
            Status: <span className="text-emerald-400 font-semibold">{workspace.status}</span>
          </div>
        </div>

        {/* 7-Tab Research Workspace UI Deck */}
        <nav className="flex space-x-1 border-t border-slate-800/80 pt-3">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`rounded-lg px-4 py-2 text-xs font-medium transition-all ${
                activeTab === tab
                  ? "bg-slate-800 text-indigo-400 shadow border border-slate-700 font-semibold"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </header>

      {/* Main Tab Content */}
      <main className="p-8">
        {activeTab === "Overview" && (
          <div className="space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-6">
              <h3 className="text-base font-semibold text-slate-200 mb-2">Workspace Overview</h3>
              <p className="text-sm text-slate-400 mb-4">
                {workspace.description || "No detailed description provided for this research session."}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-800">
                <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="text-xs text-slate-500">Research Mode</div>
                  <div className="text-lg font-bold text-white mt-1">{workspace.research_mode}</div>
                </div>
                <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="text-xs text-slate-500">Uploaded Documents</div>
                  <div className="text-lg font-bold text-indigo-400 mt-1">{documents.length}</div>
                </div>
                <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800">
                  <div className="text-xs text-slate-500">Created Date</div>
                  <div className="text-sm font-semibold text-slate-300 mt-1">
                    {new Date(workspace.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "Plan" && (
          <div className="rounded-xl border border-slate-800 bg-slate-800/30 p-8 text-center text-slate-400">
            <h3 className="text-base font-semibold text-white mb-2">Interactive Research Planning Shell</h3>
            <p className="text-xs text-slate-500">
              In Phase 3, the Planner Agent will generate structured research plans requiring HITL approval here.
            </p>
          </div>
        )}

        {activeTab === "Documents" && (
          <div className="space-y-6">
            {token && (
              <DocumentUpload
                workspaceId={workspace.id}
                token={token}
                onUploaded={() => fetchDocuments(token)}
              />
            )}

            <div className="rounded-xl border border-slate-800 bg-slate-800/40 p-6">
              <h3 className="text-base font-semibold mb-4">Workspace Documents ({documents.length})</h3>
              {documents.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">
                  No documents uploaded to this workspace yet.
                </p>
              ) : (
                <div className="divide-y divide-slate-800">
                  {documents.map((doc) => (
                    <div key={doc.id} className="py-3 flex justify-between items-center text-xs">
                      <div>
                        <div className="font-medium text-slate-200">{doc.filename}</div>
                        <div className="text-slate-500 mt-0.5">
                          {doc.mime_type} • {(doc.file_size / 1024).toFixed(1)} KB
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="text-red-400 hover:text-red-300 transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "Evidence" && (
          <div className="rounded-xl border border-slate-800 bg-slate-800/30 p-8 text-center text-slate-400">
            <h3 className="text-base font-semibold text-white mb-2">Relational EKG Visualizer Shell</h3>
            <p className="text-xs text-slate-500">
              Evidence Knowledge Graph nodes and claims visualizer will render here in Phase 2 & Phase 5.
            </p>
          </div>
        )}

        {activeTab === "Timeline" && (
          <div className="rounded-xl border border-slate-800 bg-slate-800/30 p-8 text-center text-slate-400">
            <h3 className="text-base font-semibold text-white mb-2">Execution Timeline Shell</h3>
            <p className="text-xs text-slate-500">
              Real-time LangGraph execution agent events and SSE streams will render here in Phase 3.
            </p>
          </div>
        )}

        {activeTab === "Report" && (
          <div className="rounded-xl border border-slate-800 bg-slate-800/30 p-8 text-center text-slate-400">
            <h3 className="text-base font-semibold text-white mb-2">Versioned Reports Shell</h3>
            <p className="text-xs text-slate-500">
              Final synthesized reports with Citation Explorer drawer will render here in Phase 4 & Phase 5.
            </p>
          </div>
        )}

        {activeTab === "Metrics" && (
          <div className="rounded-xl border border-slate-800 bg-slate-800/30 p-8 text-center text-slate-400">
            <h3 className="text-base font-semibold text-white mb-2">LLMOps Metrics & Telemetry Shell</h3>
            <p className="text-xs text-slate-500">
              Ragas evaluation metrics, token costs, and latency metrics will render here in Phase 6.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
