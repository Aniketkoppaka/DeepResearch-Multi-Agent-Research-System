import React, { useMemo } from "react";
import {

  ChevronLeft,
  ChevronRight,
  LogOut,
  MoreHorizontal,
  Pencil,
  Plus,
  Trash2,
  User,
  Zap,
  Search,
  GraduationCap,
  Sparkles,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Session } from "@/lib/research-data";

const GROUPS = ["Today", "Previous 7 Days", "Older"] as const;

type Props = {
  open: boolean;
  onToggle: () => void;
  sessions: Session[];
  activeId: string | null;
  user: { email: string; full_name?: string } | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onRename: (id: string) => void;
  onDelete: (id: string) => void;
  onAuthClick: () => void;
  onLogout: () => void;
};

export function Sidebar({
  open,
  onToggle,
  sessions,
  activeId,
  user,
  onSelect,
  onNew,
  onRename,
  onDelete,
  onAuthClick,
  onLogout,
}: Props) {
  const grouped = useMemo(
    () => GROUPS.map((g) => [g, sessions.filter((s) => s.group === g)] as const),
    [sessions],
  );

  const getModeIcon = (mode: Session["mode"]) => {
    switch (mode) {
      case "quick":
        return <Zap className="size-3.5 text-cyan-400 shrink-0" />;
      case "deep":
        return <Search className="size-3.5 text-blue-400 shrink-0" />;
      case "academic":
        return <GraduationCap className="size-3.5 text-purple-400 shrink-0" />;
      default:
        return <Sparkles className="size-3.5 text-emerald-400 shrink-0" />;
    }
  };

  return (
    <aside
      className={`z-20 flex h-full shrink-0 flex-col border-r border-white/10 bg-[#171717] transition-all duration-300 ease-in-out ${
        open ? "w-[260px]" : "w-[60px]"
      }`}
    >
      <div className="flex h-full w-full flex-col p-2.5">
        {/* Header */}
        <div className="flex items-center justify-between px-1 py-1">
          {open ? (
            <button
              onClick={onNew}
              className="flex items-center gap-2 text-sm font-semibold text-white transition-opacity hover:opacity-80"
            >
              <div className="flex size-7 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">
                <Sparkles className="size-4" />
              </div>
              <span>DeepResearch</span>
            </button>
          ) : (
            <button
              onClick={onNew}
              title="DeepResearch"
              className="mx-auto flex size-8 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400"
            >
              <Sparkles className="size-4" />
            </button>
          )}

          <button
            onClick={onToggle}
            aria-label={open ? "Collapse sidebar" : "Expand sidebar"}
            className="flex size-8 items-center justify-center rounded-lg text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-white"
          >
            {open ? <ChevronLeft className="size-4" /> : <ChevronRight className="size-4" />}
          </button>
        </div>

        {/* New Research Button */}
        <div className="mt-3">
          {open ? (
            <button
              onClick={onNew}
              className="flex w-full items-center justify-between rounded-xl border border-white/10 bg-[#212121] px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-neutral-800 cursor-pointer"
            >
              <span className="flex items-center gap-2">
                <Plus className="size-3.5" />
                <span>New Research</span>
              </span>
              <kbd className="rounded bg-neutral-800 px-1.5 py-0.5 font-mono text-[10px] text-neutral-400">
                ⌘K
              </kbd>
            </button>
          ) : (
            <button
              onClick={onNew}
              title="New Research"
              className="flex size-9 mx-auto items-center justify-center rounded-xl border border-white/10 bg-[#212121] text-white hover:bg-neutral-800 cursor-pointer"
            >
              <Plus className="size-4" />
            </button>
          )}
        </div>

        {/* History List */}
        {open && (
          <div className="mt-4 flex-1 space-y-4 overflow-y-auto pr-1">
            {grouped.map(([group, list]) =>
              list.length === 0 ? null : (
                <div key={group}>
                  <p className="px-2 text-[11px] font-semibold text-neutral-500">{group}</p>
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
                            className="flex flex-1 items-center gap-2 truncate px-2.5 py-2 text-left cursor-pointer"
                          >
                            {getModeIcon(s.mode)}
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
        )}

        {!open && <div className="flex-1" />}

        {/* User Account / Sign In section */}
        <div className="mt-auto border-t border-white/10 pt-2">
          {user ? (
            open ? (
              <div className="flex items-center justify-between rounded-xl px-2 py-2 text-xs hover:bg-neutral-800/60">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="flex size-7 items-center justify-center rounded-full bg-emerald-600 font-semibold text-white">
                    {user.full_name ? user.full_name[0].toUpperCase() : user.email[0].toUpperCase()}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-white">{user.full_name || "User"}</p>
                    <p className="truncate text-[11px] text-neutral-400">{user.email}</p>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  title="Log out"
                  className="rounded p-1 text-neutral-400 hover:bg-neutral-700 hover:text-white"
                >
                  <LogOut className="size-3.5" />
                </button>
              </div>
            ) : (
              <button
                onClick={onLogout}
                title={`Signed in as ${user.email} (Click to log out)`}
                className="mx-auto flex size-8 items-center justify-center rounded-full bg-emerald-600 font-semibold text-white"
              >
                {user.full_name ? user.full_name[0].toUpperCase() : user.email[0].toUpperCase()}
              </button>
            )
          ) : open ? (
            <button
              onClick={onAuthClick}
              className="flex w-full items-center gap-2.5 rounded-xl border border-white/10 bg-[#212121] px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-neutral-800 cursor-pointer"
            >
              <div className="flex size-6 items-center justify-center rounded-full bg-neutral-800 text-neutral-300">
                <User className="size-3.5" />
              </div>
              <div className="text-left">
                <p className="font-semibold text-white">Sign In / Register</p>
                <p className="text-[10px] text-neutral-400">Save your research history</p>
              </div>
            </button>
          ) : (
            <button
              onClick={onAuthClick}
              title="Sign In / Register"
              className="mx-auto flex size-8 items-center justify-center rounded-full bg-neutral-800 text-neutral-300 hover:bg-neutral-700 hover:text-white cursor-pointer"
            >
              <User className="size-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}
