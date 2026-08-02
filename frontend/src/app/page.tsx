import React from "react";
import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex flex-col min-h-screen items-center justify-center p-24 bg-slate-950 text-white">
      <h1 className="text-6xl font-bold mb-4">DeepResearch</h1>
      <p className="text-xl text-slate-400 mb-8 max-w-2xl text-center">
        An enterprise-grade, multi-agent AI research platform for deep,
        citation-backed literature reviews and synthesis.
      </p>
      <div className="flex gap-4">
        <Link
          href="/dashboard"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-md font-medium"
        >
          Go to Dashboard
        </Link>
        <Link
          href="/login"
          className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-md font-medium"
        >
          Login
        </Link>
      </div>
    </main>
  );
}
