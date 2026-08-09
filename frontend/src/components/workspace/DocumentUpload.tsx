"use client";

import { useState } from "react";

interface DocumentUploadProps {
  workspaceId: string;
  token: string;
  onUploaded: () => void;
}

export default function DocumentUpload({
  workspaceId,
  token,
  onUploaded,
}: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    setUploading(true);
    setProgress(20);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      setProgress(50);
      const res = await fetch(`http://localhost:8000/api/v1/workspaces/${workspaceId}/documents`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to upload document");
      }

      setProgress(100);
      onUploaded();
    } catch (err: any) {
      setError(err.message || "Document upload failed");
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-800/30 p-6">
      <h3 className="text-base font-semibold mb-2">Upload Research Documents</h3>
      <p className="text-xs text-slate-400 mb-4">
        Supports PDF, DOCX, and TXT files up to 25MB. Files are validated using header signature checks.
      </p>

      {error && (
        <div className="mb-4 rounded bg-red-500/10 border border-red-500/20 p-3 text-xs text-red-400">
          {error}
        </div>
      )}

      <div className="relative border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-lg p-8 text-center transition-colors">
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileChange}
          disabled={uploading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
        />
        <div className="pointer-events-none">
          <p className="text-sm font-medium text-slate-300">
            {uploading ? `Uploading... ${progress}%` : "Drop files here or click to browse"}
          </p>
          <p className="text-xs text-slate-500 mt-1">PDF, DOCX, TXT max 25MB</p>
        </div>
      </div>

      {uploading && (
        <div className="mt-4 h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
}
