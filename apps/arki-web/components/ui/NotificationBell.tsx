"use client";

import { useEffect, useRef, useState } from "react";
import { Bell, X } from "lucide-react";
import { dashboardApi } from "@/lib/api";
import { cn } from "@/lib/cn";

interface Notification {
  id: string;
  message: string;
  type: "warning" | "info" | "error";
  createdAt: string;
  read: boolean;
}

interface SummaryData {
  low_stock_count?: number;
  new_leads_today?: number;
  pending_capacity?: number;
  pending_deliveries?: number;
  [key: string]: unknown;
}

let notifIdCounter = 0;
function genId() {
  return `notif-${++notifIdCounter}-${Date.now()}`;
}

export default function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const prevSummary = useRef<SummaryData | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function poll() {
      dashboardApi
        .summary()
        .then((res) => {
          const current: SummaryData = res.data?.data ?? {};
          const prev = prevSummary.current;
          if (prev !== null) {
            const newNotifs: Notification[] = [];
            if (
              (current.low_stock_count ?? 0) > (prev.low_stock_count ?? 0)
            ) {
              newNotifs.push({
                id: genId(),
                message: `재고 부족 상품이 ${current.low_stock_count}개로 증가했습니다.`,
                type: "warning",
                createdAt: new Date().toISOString(),
                read: false,
              });
            }
            if ((current.new_leads_today ?? 0) > (prev.new_leads_today ?? 0)) {
              newNotifs.push({
                id: genId(),
                message: `신규 문의가 ${current.new_leads_today}건으로 증가했습니다.`,
                type: "info",
                createdAt: new Date().toISOString(),
                read: false,
              });
            }
            if (
              (current.pending_capacity ?? 0) === 0 &&
              (prev.pending_capacity ?? 0) > 0
            ) {
              newNotifs.push({
                id: genId(),
                message: "배송 가능 CAPA가 0이 되었습니다.",
                type: "error",
                createdAt: new Date().toISOString(),
                read: false,
              });
            }
            if (newNotifs.length > 0) {
              setNotifications((prev) => [...newNotifs, ...prev].slice(0, 50));
            }
          }
          prevSummary.current = current;
        })
        .catch(() => {});
    }

    poll();
    const timer = setInterval(poll, 60_000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  const unread = notifications.filter((n) => !n.read).length;

  function markAllRead() {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  function dismiss(id: string) {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }

  const typeColors: Record<Notification["type"], string> = {
    warning: "text-amber-600 bg-amber-50",
    info: "text-blue-600 bg-blue-50",
    error: "text-red-600 bg-red-50",
  };

  return (
    <div className="relative" ref={panelRef}>
      <button
        onClick={() => {
          setOpen((v) => !v);
          if (!open) markAllRead();
        }}
        className="relative flex h-8 w-8 items-center justify-center rounded-md text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
        aria-label="알림"
      >
        <Bell className="h-5 w-5" />
        {unread > 0 && (
          <span className="absolute right-0.5 top-0.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-red-500 px-0.5 text-[10px] font-bold text-white">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-10 z-50 w-80 rounded-lg border border-slate-200 bg-white shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <span className="text-sm font-semibold text-slate-800">알림</span>
            {notifications.length > 0 && (
              <button
                onClick={() => setNotifications([])}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                모두 지우기
              </button>
            )}
          </div>

          <ul className="max-h-80 divide-y divide-slate-100 overflow-y-auto">
            {notifications.length === 0 ? (
              <li className="px-4 py-6 text-center text-sm text-slate-400">
                알림이 없습니다
              </li>
            ) : (
              notifications.map((n) => (
                <li
                  key={n.id}
                  className={cn(
                    "flex items-start gap-3 px-4 py-3",
                    !n.read && "bg-slate-50"
                  )}
                >
                  <span
                    className={cn(
                      "mt-0.5 rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase",
                      typeColors[n.type]
                    )}
                  >
                    {n.type === "warning"
                      ? "경고"
                      : n.type === "error"
                        ? "오류"
                        : "정보"}
                  </span>
                  <span className="flex-1 text-xs text-slate-700">
                    {n.message}
                  </span>
                  <button
                    onClick={() => dismiss(n.id)}
                    className="mt-0.5 shrink-0 text-slate-300 hover:text-slate-500"
                    aria-label="닫기"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
