import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-white p-4">
      <h1 className="text-4xl font-bold mb-2">404</h1>
      <h2 className="text-xl font-semibold mb-4">Page Not Found</h2>
      <p className="text-slate-400 mb-6">The requested resource does not exist.</p>
      <Linh
        href="/"
        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-md"
      >
        Return Home
      </Link>
    </div>
  );
}
