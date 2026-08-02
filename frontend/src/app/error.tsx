"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-white p-4">
      <h1 className="text-2xl font-bold mb-4">Something went wrong!</h1>
      <p className="text-slate-400 mb-6">{error.message}</p>
      <button
        onClick={() => reset()}
        className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded-md"
      >
        Try Again
      </button>
    </div>
  );
}
