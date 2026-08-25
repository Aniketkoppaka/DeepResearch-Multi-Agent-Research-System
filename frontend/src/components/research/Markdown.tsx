import { Fragment, type ReactNode } from "react";

/** Minimal markdown renderer with interactive [n] citation tags. */
export function Markdown({
  source,
  onCite,
}: {
  source: string;
  onCite?: (id: number) => void;
}) {
  const inline = (text: string, key: string) => {
    const parts = text.split(/(\[\d+\]|\*\*[^*]+\*\*)/g).filter(Boolean);
    return parts.map((p, i) => {
      const cite = p.match(/^\[(\d+)\]$/);
      if (cite) {
        const id = Number(cite[1]);
        return (
          <button
            key={`${key}-${i}`}
            onClick={() => onCite?.(id)}
            className="mx-0.5 inline-flex h-[18px] min-w-[18px] items-center justify-center rounded-md bg-emerald-500/15 px-1 align-[1px] text-[11px] font-semibold text-emerald-400 transition-colors hover:bg-emerald-500/30 cursor-pointer"
          >
            {id}
          </button>
        );
      }
      if (p.startsWith("**") && p.endsWith("**")) {
        return <strong key={`${key}-${i}`} className="font-semibold text-white">{p.slice(2, -2)}</strong>;
      }
      return <Fragment key={`${key}-${i}`}>{p}</Fragment>;
    });
  };

  const nodes: ReactNode[] = [];
  let list: string[] = [];

  const flushList = (key: string) => {
    if (!list.length) return;
    const items = list;
    list = [];
    nodes.push(
      <ul key={`ul-${key}`} className="list-disc pl-5 space-y-1 my-2 text-neutral-300">
        {items.map((line, li) => (
          <li key={li}>{inline(line, `${key}-${li}`)}</li>
        ))}
      </ul>,
    );
  };

  source.split("\n").forEach((raw, i) => {
    const line = raw.trim();
    if (line.startsWith("- ")) {
      list.push(line.slice(2));
      return;
    }
    flushList(String(i));
    if (!line) return;
    if (line.startsWith("### ")) nodes.push(<h3 key={i} className="text-base font-semibold mt-4 mb-1 text-white">{line.slice(4)}</h3>);
    else if (line.startsWith("## ")) nodes.push(<h2 key={i} className="text-lg font-semibold mt-6 mb-2 text-emerald-400">{line.slice(3)}</h2>);
    else if (line.startsWith("# ")) nodes.push(<h1 key={i} className="text-xl font-bold mb-4 text-white">{line.slice(2)}</h1>);
    else nodes.push(<p key={i} className="my-2 leading-relaxed text-neutral-300">{inline(line, String(i))}</p>);
  });
  flushList("end");

  return <div className="prose-research text-[15px]">{nodes}</div>;
}
