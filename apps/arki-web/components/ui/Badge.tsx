"use client";

import { cn } from "@/lib/cn";

type BadgeVariant =
  | "green"
  | "blue"
  | "yellow"
  | "red"
  | "gray"
  | "purple"
  | "indigo";

const variantStyles: Record<BadgeVariant, string> = {
  green: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  blue: "bg-blue-50 text-blue-700 ring-blue-600/20",
  yellow: "bg-amber-50 text-amber-700 ring-amber-600/20",
  red: "bg-red-50 text-red-700 ring-red-600/20",
  gray: "bg-gray-50 text-gray-600 ring-gray-500/20",
  purple: "bg-purple-50 text-purple-700 ring-purple-600/20",
  indigo: "bg-indigo-50 text-indigo-700 ring-indigo-600/20",
};

/** Map common status strings to badge colors */
const statusColorMap: Record<string, BadgeVariant> = {
  // green
  active: "green",
  completed: "green",
  success: "green",
  open: "green",
  approved: "green",
  signed: "green",
  confirmed: "green",
  paid: "green",
  normal: "green",
  converted: "green",
  // blue
  in_progress: "blue",
  in_transit: "blue",
  new: "blue",
  ordered: "blue",
  shipped: "blue",
  invoiced: "blue",
  partially_paid: "blue",
  // yellow
  pending: "yellow",
  draft: "yellow",
  scheduled: "yellow",
  requested: "yellow",
  reviewed: "yellow",
  delayed: "yellow",
  limited: "yellow",
  maintenance: "yellow",
  low_stock: "yellow",
  repeat: "yellow",
  // red
  cancelled: "red",
  rejected: "red",
  error: "red",
  full: "red",
  out_of_stock: "red",
  dropped: "red",
  unpaid: "red",
  // gray
  inactive: "gray",
  closed: "gray",
  created: "gray",
  inbound_pending: "gray",
  // purple
  vip: "purple",
  converted_to_order: "purple",
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  /** Auto-detect variant from status string */
  status?: string;
  className?: string;
}

export default function Badge({
  children,
  variant,
  status,
  className,
}: BadgeProps) {
  const resolvedVariant =
    variant ?? (status ? statusColorMap[status] ?? "gray" : "gray");

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset",
        variantStyles[resolvedVariant],
        className
      )}
    >
      {children}
    </span>
  );
}
