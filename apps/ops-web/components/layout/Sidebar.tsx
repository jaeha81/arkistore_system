"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderKanban,
  AlertTriangle,
  ScrollText,
  Rocket,
} from "lucide-react";
import { cn } from "../../lib/utils";

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

const navItems = [
  {
    label: "대시보드",
    href: "/ops",
    icon: LayoutDashboard,
    exact: true,
  },
  {
    label: "프로젝트 관리",
    href: "/ops/projects",
    icon: FolderKanban,
  },
  {
    label: "오류/이슈 관리",
    href: "/ops/issues",
    icon: AlertTriangle,
  },
  {
    label: "이벤트/오류 로그",
    href: "/ops/logs",
    icon: ScrollText,
  },
  {
    label: "배포 기록",
    href: "/ops/deployments",
    icon: Rocket,
  },
];

export default function Sidebar({ open = false, onClose }: SidebarProps) {
  const pathname = usePathname();

  function isActive(href: string, exact?: boolean) {
    if (exact) return pathname === href;
    return pathname === href || pathname.startsWith(href + "/");
  }

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 flex h-screen w-60 flex-col bg-slate-800 transition-transform duration-200",
        "md:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}
    >
      <div className="flex h-16 items-center justify-between px-5">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-bold text-white">
            JH
          </div>
          <span className="text-sm font-semibold text-white">운영 대시보드</span>
        </div>
        <button
          onClick={onClose}
          className="flex h-7 w-7 items-center justify-center rounded text-slate-400 hover:text-white md:hidden"
          aria-label="닫기"
        >
          ✕
        </button>
      </div>

      <nav className="mt-2 flex-1 space-y-1 px-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href, item.exact);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-slate-700 text-white"
                  : "text-slate-300 hover:bg-slate-700/50 hover:text-white"
              )}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-slate-700 px-5 py-4">
        <p className="text-xs text-slate-500">© 2024 JH Operations</p>
      </div>
    </aside>
  );
}
