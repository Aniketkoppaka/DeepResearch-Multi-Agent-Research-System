import React, { useRef, useState } from "react";
import { ArrowUp, Globe, Paperclip, X, Zap, Search, GraduationCap } from "lucide-react";

import { MODES, type ResearchMode } from "@/lib/research-data";

type Props = {
  onSend: (text: string, files: string[], mode: ResearchMode, webSearch: boolean) => void;
  disabled?: boolean;
  placeholder?: string;
  selectedMode: ResearchMode;
  onModeChange: (mode: ResearchMode) => void;
};

export function Composer({
  onSend,
  disabled,
  placeholder,
  selectedMode,
  onModeChange,
}: Props) {
  const [value, setValue] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  const [web, setWeb] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  const send = () => {
    if (!value.trim() || disabled) return;
    onSend(value.trim(), files, selectedMode, web);
    setValue("");
    setFiles([]);
  };

  const getModeIcon = (modeId: ResearchMode) => {
    switch (modeId) {
      case "quick":
        return <Zap className="size-3" />;
      case "deep":
        return <Search className="size-3" />;
      case "academic":
        return <GraduationCap className="size-3" />;
    }
  };

  return (
    <div className="surface-panel glow-ring rounded-2xl p-3 bg-[#212121] border border-white/10 shadow-2xl">
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 px-1 pb-2">
          {files.map((f) => (
            <span
              key={f}
              className="flex items-center gap-1.5 rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-200 border border-white/5"
            >
              <Paperclip className="size-3" />
              {f}
              <button
                onClick={() => setFiles((p) => p.filter((x) => x !== f))}
                aria-label={`Remove ${f}`}
                className="hover:text-red-400"
              >
                <X className="size-3" />
              </button>
            </span>
          ))}
        </div>
      )}

      <textarea
        rows={2}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            send();
          }
        }}
        placeholder={placeholder ?? "Describe the topic you want researched…"}
        className="max-h-40 w-full resize-none bg-transparent px-2 py-1 text-[15px] leading-relaxed text-white outline-none placeholder:text-neutral-500"
      />

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-white/5 pt-2.5 mt-1">
        {/* Left Toolbar: File upload, Web search toggle, Research Mode Selector */}
        <div className="flex items-center gap-1.5">
          <input
            ref={inputRef}
            type="file"
            multiple
            className="hidden"
            onChange={(e) => {
              const list = Array.from(e.target.files ?? []).map((f) => f.name);
              setFiles((p) => [...p, ...list]);
              e.target.value = "";
            }}
          />
          <button
            onClick={() => inputRef.current?.click()}
            title="Attach documents (PDF, DOCX, TXT)"
            className="flex size-8 items-center justify-center rounded-lg text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white cursor-pointer"
          >
            <Paperclip className="size-4" />
          </button>

          <button
            onClick={() => setWeb((w) => !w)}
            title="Toggle real-time web search"
            className={`flex h-7 items-center gap-1.5 rounded-lg px-2.5 text-xs font-medium transition-colors cursor-pointer ${
              web
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                : "text-neutral-400 hover:bg-neutral-800 border border-transparent"
            }`}
          >
            <Globe className="size-3.5" />
            <span>Web search</span>
          </button>

          {/* Inline Mode Selector */}
          <div className="flex items-center gap-1 bg-neutral-900/80 p-0.5 rounded-lg border border-white/5 ml-1">
            {MODES.map((m) => {
              const sel = m.id === selectedMode;
              return (
                <button
                  key={m.id}
                  onClick={() => onModeChange(m.id)}
                  title={m.hint}
                  className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
                    sel
                      ? "bg-neutral-800 text-white shadow-sm font-semibold"
                      : "text-neutral-400 hover:text-neutral-200"
                  }`}
                >
                  {getModeIcon(m.id)}
                  <span>{m.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Action: Send Button */}
        <button
          onClick={send}
          disabled={!value.trim() || disabled}
          aria-label="Send message"
          className="flex size-8 items-center justify-center rounded-full bg-white text-black transition-opacity disabled:opacity-30 hover:opacity-90 cursor-pointer shrink-0"
        >
          <ArrowUp className="size-4" />
        </button>
      </div>
    </div>
  );
}
