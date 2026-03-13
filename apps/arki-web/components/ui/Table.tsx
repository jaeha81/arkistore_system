"use client";

import { cn } from "@/lib/cn";

/* ─── Generic Table ─── */

interface Column<T> {
  key: string;
  header: string;
  /** Custom render for a cell. Falls back to row[key] */
  render?: (row: T) => React.ReactNode;
  className?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  /** Key field for row identity */
  rowKey?: string;
  onRowClick?: (row: T) => void;
  emptyText?: string;
  className?: string;
}

export type { Column };

export default function Table<T extends Record<string, unknown>>({
  columns,
  data,
  rowKey = "id",
  onRowClick,
  emptyText = "데이터가 없습니다.",
  className,
}: TableProps<T>) {
  return (
    <div className={cn("overflow-x-auto rounded-lg border border-slate-200", className)}>
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={cn(
                  "whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500",
                  col.className
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-10 text-center text-sm text-slate-400"
              >
                {emptyText}
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr
                key={(row[rowKey] as string) ?? idx}
                onClick={() => onRowClick?.(row)}
                className={cn(
                  "transition-colors hover:bg-slate-50",
                  onRowClick && "cursor-pointer"
                )}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={cn(
                      "whitespace-nowrap px-4 py-3 text-sm text-slate-700",
                      col.className
                    )}
                  >
                    {col.render
                      ? col.render(row)
                      : (row[col.key] as React.ReactNode) ?? "—"}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
