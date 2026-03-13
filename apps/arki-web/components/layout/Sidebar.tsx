"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/cn";
import {
  LayoutDashboard,
  Package,
  Warehouse,
  ClipboardList,
  FileText,
  Receipt,
  Ship,
  Users,
  MessageSquare,
  Handshake,
  FileSignature,
  Truck,
  CalendarClock,
  Phone,
} from "lucide-react";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

const iconCls = "h-4 w-4";

const navGroups: NavGroup[] = [
  {
    title: "메인",
    items: [
      {
        label: "대시보드",
        href: "/arki/dashboard",
        icon: <LayoutDashboard className={iconCls} />,
      },
    ],
  },
  {
    title: "물류 사이트",
    items: [
      {
        label: "상품 마스터",
        href: "/arki/products",
        icon: <Package className={iconCls} />,
      },
      {
        label: "재고 현황",
        href: "/arki/inventory",
        icon: <Warehouse className={iconCls} />,
      },
      {
        label: "발주 요청",
        href: "/arki/purchase-requests",
        icon: <ClipboardList className={iconCls} />,
      },
      {
        label: "발주서 관리",
        href: "/arki/purchase-orders",
        icon: <FileText className={iconCls} />,
      },
      {
        label: "인보이스",
        href: "/arki/invoices",
        icon: <Receipt className={iconCls} />,
      },
      {
        label: "BL/선적 관리",
        href: "/arki/shipments",
        icon: <Ship className={iconCls} />,
      },
    ],
  },
  {
    title: "영업 사이트",
    items: [
      {
        label: "고객 관리",
        href: "/arki/customers",
        icon: <Users className={iconCls} />,
      },
      {
        label: "문의/리드",
        href: "/arki/leads",
        icon: <MessageSquare className={iconCls} />,
      },
    ],
  },
  {
    title: "판매매니저",
    items: [
      {
        label: "상담 관리",
        href: "/arki/consultations",
        icon: <Handshake className={iconCls} />,
      },
      {
        label: "계약 관리",
        href: "/arki/contracts",
        icon: <FileSignature className={iconCls} />,
      },
      {
        label: "배송 관리",
        href: "/arki/deliveries",
        icon: <Truck className={iconCls} />,
      },
      {
        label: "배송 CAPA",
        href: "/arki/capacity-slots",
        icon: <CalendarClock className={iconCls} />,
      },
      {
        label: "해피콜",
        href: "/arki/happy-calls",
        icon: <Phone className={iconCls} />,
      },
    ],
  },
];

export default function Sidebar({ open = false, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 flex h-full w-60 flex-col border-r border-slate-200 bg-slate-900 transition-transform duration-200",
        "md:relative md:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
      )}
    >
      <div className="flex h-14 items-center justify-between border-b border-slate-700 px-5">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-blue-600 text-xs font-bold text-white">
            A
          </div>
          <span className="text-base font-bold tracking-tight text-white">
            Arkistore
          </span>
        </div>
        <button
          onClick={onClose}
          className="flex h-7 w-7 items-center justify-center rounded text-slate-400 hover:text-white md:hidden"
          aria-label="닫기"
        >
          ✕
        </button>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {navGroups.map((group) => (
          <div key={group.title} className="mb-4">
            <p className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
              {group.title}
            </p>
            {group.items.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm font-medium transition-colors",
                    active
                      ? "bg-slate-800 text-white"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                  )}
                >
                  {item.icon}
                  {item.label}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
