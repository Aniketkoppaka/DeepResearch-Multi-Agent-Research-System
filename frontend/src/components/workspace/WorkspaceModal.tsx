"use client";

import { useState } from "react";

interface WorkspaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
  token: string;
}

export default function WorkspaceModal({
  isOpen,
  onClose,
  onCreated,
  token,
}: WorkspaceModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [researchMode, setResearchMode] = useState<"Quick" | "Deep" | "Academic">("Deep");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/workspaces", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title,
          description: description || undefined,
          research_mode: researchMode,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to create workspace");
      }

      setTitle("");
      setDescription("");
      onCreated();
      onClose();
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-xl border border-slate-700 bg-slate-800 p-6 shadow-2xl text-white">
        <div className="flex items-center justify-between border-b border-slate-700 pb-4 mb-4">
          <h2 className="text-xl font-bold">Create New Workspace</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Workspace Title *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Autonomous AI Agents Survey"
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Description (Optional)
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of research scope and objectives..."
              className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Research Mode
            </label>
            <div className="grid grid-cols-3 gap-3">
              {(["Quick", "Deep", "Academic"] as const).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setResearchMode(mode)}
                  className={`rounded-lg border p-3 text-left transition-all ${
                    researchMode === mode
                      ? "border-indigo-500 bg-indigo-500/10 text-white"
                      : "border-slate-700 bg-slate-900 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  <div className="font-semibold text-sm">{mode}</div>
                  <div className="text-[10px] text-slate-500 mt-1">
                    {mode === "Quick" && "Fast web summary"}
                    {mode === "Deep" && "Multi-agent RAG"}
                    {mode === "Academic" && "Peer-reviewed literature"}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-700">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md px-4 py-2 text-sm font-medium text-slate-400 hover:bg-slate-700 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !title.trim()}
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
            >
              {loading ? "Creating..." : "Create Workspace"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
