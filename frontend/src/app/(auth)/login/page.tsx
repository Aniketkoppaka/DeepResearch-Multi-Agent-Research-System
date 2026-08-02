import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
      <div className="w-full max-w-md p-8 bg-slate-900 rounded-lg border border-slate-800">
        <h1 className="text-2xl font-bold mb-6 text-center">Sign In to DeepResearch</h1>
        <p className="text-sm text-slate-400 mb-6 text-center">
          Authentication will be implemented in Milestone 1.2
        </p>
        <Link
          href="/dashboard"
          className="block ww-full py-3 bg-blue-600 hover:bg-blue-500 rounded-md text-center font-medium"
        >
          Bybpass to Dashboard
        </Link>
      </div>
    </div>
  );
}
