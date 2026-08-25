import { useMemo } from "react";
import {
  ChevronsLeft,
  LogOut,
  MoreHorizontal,
  Pencil,
  PanelLeft,
  Plus,
  Settings,
  Trash2,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Session } from "@/lib/research-data";

const MODE_ICON: Record<Session["mode"], string> = {
  quick: "⚡",
  deep: "🔍",
  academic: "🎓",
};

const GROUPS = ["Today", "Previous 7 Days", "Older"] as const;

type Props = {
  open: boolean;
  onToggle: () => void;
  sessions: Session[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onRename: (id: string) => void;
  onDelete: (id: string) => void;
};

export function Sidebar({
  open,
  onToggle,
  sessions,
  activeId,
  onSelect,
  onNew,
  onRename,
  onDelete,
}: Props) {
  const grouped = useMemo(
    () => GROUPS.map((g) => [g, sessions.filter((s) => s.group === g)] as const),
    [sessions],
  );

  return (
    <>
      {!open && (
        <div className="absolute left-3 top-3 z-30 flex items-center gap-1">
          <button
            onClick={onToggle}
            aria-label="Open sidebar"
            className="flex size-9 items-center justify-center rounded-lg text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white"
          >
            <PanelLeft className="size-4" />
          </button>
          <button
            onClick={onNew}
            aria-label="New research"
            className="flex size-9 items-center justify-center rounded-lg text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white"
          >
            <Plus className="size-4" />
          </button>
        </div>
      )}

      <aside
        className={`z-20 flex h-full shrink-0 flex-col border-r border-white/10 bg-[#171717] transition-[width,margin] duration-300 ease-out ${
          open ? "w-[260px]" : "w-0 -mr-px overflow-hidden"
        }`}
      >
        <div className="flex h-full w-[260px] flex-col p-3">
          <div className="flex items-center justify-between px-2 py-1">
            <button
              onClick={onNew}
              className="flex items-center gap-2 text-sm font-semibold text-white transition-opacity hover:opacity-80"
            >
              <div className="flex size-6 items-center justify-center rounded-md bg-emerald-500/15 text-xs text-emerald-400">
                DR
              </div>
              <span>DeepResearch</span>
            </button>
            <button
              onClick={onToggle}
              aria-label="Collapse sidebar"
              className="rounded-lg p-1.5 text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white"
            >
              <ChevronsLeft className="size-4" />
            </button>
          </div>

          <button
            onClick={onNew}
            className="mt-3 flex items-center justify-between rounded-xl border border-white/10 bg-[#212121] px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-neutral-800"
          >
            <span className="flex items-center gap-2">
              <Plus className="size-3.5" />
              <span>New Research</span>
            </span>
            <kbd className="rounded bg-neutral-800 px-1.5 py-0.5 font-mono text-[10px] text-neutral-400">
              ⌘K
            </kbd>
          </button>

          <div className="mt-4 flex-1 space-y-4 overflow-y-auto pr-1">
            {grouped.map(([group, list]) =>
              list.length === 0 ? null : (
                <div key={group}>
                  <p className="px-2 text-[11px] font-semibold text-neutral-500">
                    {group}
                  </p>
                  <ul className="mt-1 space-y-0.5">
                    {list.map((s) => {
                      const active = s.id === activeId;
                      return (
                        <li
                          key={s.id}
                          className={`group relative flex items-center rounded-lg text-xs transition-colors ${
                            active
                              ? "bg-neutral-800 font-medium text-white"
                              : "text-neutral-300 hover:bg-neutral-800/60 hover:text-white"
                          }`}
                        >
                          <button
                            onClick={() => onSelect(s.id)}
                            className="flex flex-1 items-center gap-2 truncate px-2.5 py-2 text-left"
                          >
                            <span className="text-xs">{MODE_ICON[s.mode]}</span>
                            <span className="truncate">{s.title}</span>
                          </button>

                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <button
                                aria-label="Session actions"
                                className="mr-1 rounded p-1 opacity-0 transition-opacity hover:bg-neutral-700 group-hover:opacity-100 data-[state=open]:opacity-100"
                              >
                                <MoreHorizontal className="size-3.5 text-neutral-400" />
                              </button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-36">
                              <DropdownMenuItem onClick={() => onRename(s.id)}>
                                <Pencil className="mr-2 size-3.5" />
                                <span>Rename</span>
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => onDelete(s.id)}
                                className="text-red-400 focus:text-red-400"
                              >
                                <Trash2 className="mr-2 size-3.5" />
                                <span>Delete</span>
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ),
            )}
          </div>

          <div className="mt-auto border-t border-white/10 pt-2">
            <div className="flex items-center gap-2.5 rounded-xl px-2 py-2 text-xs hover:bg-neutral-800/60">
              <div className="flex size-7 items-center justify-center rounded-full bg-emerald-600 font-semibold text-white">
                A
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium text-white">Admin</p>
                <p className="truncate text-[11px] text-neutral-400">admin@gmail.com</p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
