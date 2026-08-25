import { useRef, useState } from "react";
import { ArrowUp, Globe, Paperclip, X } from "lucide-react";

type Props = {
  onSend: (text: string, files: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
};

export function Composer({ onSend, disabled, placeholder }: Props) {
  const [value, setValue] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  const [web, setWeb] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  const send = () => {
    if (!value.trim() || disabled) return;
    onSend(value.trim(), files);
    setValue("");
    setFiles([]);
  };

  return (
    <div className="surface-panel glow-ring rounded-3xl p-2 bg-[#212121] border border-white/10">
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2 px-2 pb-2 pt-1">
          {files.map((f) => (
            <span
              key={f}
              className="flex items-center gap-1.5 rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-200"
            >
              <Paperclip className="size-3" />
              {f}
              <button
                onClick={() => setFiles((p) => p.filter((x) => x !== f))}
                aria-label={`Remove ${f}`}
              >
                <X className="size-3 opacity-60 hover:opacity-100" />
              </button>
            </span>
          ))}
        </div>
      )}

      <textarea
        rows={1}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            send();
          }
        }}
        placeholder={placeholder ?? "Describe the topic you want researched…"}
        className="max-h-40 w-full resize-none bg-transparent px-3 py-2.5 text-[15px] leading-6 text-white outline-none placeholder:text-neutral-400"
      />

      <div className="flex items-center gap-1 px-1 pb-0.5">
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
          aria-label="Attach documents"
          className="flex size-8 items-center justify-center rounded-full text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white"
        >
          <Paperclip className="size-4" />
        </button>

        <button
          onClick={() => setWeb((w) => !w)}
          className={`flex h-8 items-center gap-1.5 rounded-full px-2.5 text-xs font-medium transition-colors ${
            web ? "bg-emerald-500/15 text-emerald-400" : "text-neutral-400 hover:bg-neutral-800"
          }`}
        >
          <Globe className="size-3.5" />
          <span>Web search</span>
        </button>

        <span className="flex-1" />

        <button
          onClick={send}
          disabled={!value.trim() || disabled}
          aria-label="Send message"
          className="flex size-8 items-center justify-center rounded-full bg-white text-black transition-opacity disabled:opacity-30 hover:opacity-90"
        >
          <ArrowUp className="size-4" />
        </button>
      </div>
    </div>
  );
}
