import { cn } from "../../lib/utils";

type BadgeVariant =
  | "default"
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "gray";

const variantStyles: Record<BadgeVariant, string> = {
  default:
    "bg-slate-100 text-slate-700 ring-slate-200",
  success:
    "bg-emerald-50 text-emerald-700 ring-emerald-200",
  warning:
    "bg-amber-50 text-amber-700 ring-amber-200",
  danger:
    "bg-red-50 text-red-700 ring-red-200",
  info:
    "bg-blue-50 text-blue-700 ring-blue-200",
  gray:
    "bg-gray-100 text-gray-500 ring-gray-200",
};

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

export default function Badge({
  children,
  variant = "default",
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

// Helper maps for common status → variant
export function statusVariant(
  status: string | undefined | null
): BadgeVariant {
  switch (status?.toLowerCase()) {
    case "active":
    case "resolved":
    case "success":
      return "success";
    case "maintenance":
    case "acknowledged":
    case "warning":
    case "pending":
      return "warning";
    case "error":
    case "emergency":
    case "failed":
    case "new":
      return "danger";
    case "inactive":
    case "archived":
      return "gray";
    case "dev":
    case "development":
      return "info";
    case "staging":
      return "warning";
    case "production":
      return "danger";
    default:
      return "default";
  }
}
