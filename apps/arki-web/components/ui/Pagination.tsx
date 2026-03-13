"use client";

import { cn } from "@/lib/cn";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({
  page,
  pageSize,
  total,
  onPageChange,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const canPrev = page > 1;
  const canNext = page < totalPages;

  return (
    <div className="flex items-center justify-between border-t border-slate-200 bg-white px-4 py-3">
      <p className="text-sm text-slate-500">
        총 <span className="font-medium text-slate-700">{total}</span>건 중{" "}
        <span className="font-medium text-slate-700">
          {Math.min((page - 1) * pageSize + 1, total)}
        </span>
        –
        <span className="font-medium text-slate-700">
          {Math.min(page * pageSize, total)}
        </span>
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={!canPrev}
          className={cn(
            "inline-flex items-center rounded-md p-1.5 text-sm transition-colors",
            canPrev
              ? "text-slate-600 hover:bg-slate-100"
              : "cursor-not-allowed text-slate-300"
          )}
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <span className="px-2 text-sm font-medium text-slate-700">
          {page} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!canNext}
          className={cn(
            "inline-flex items-center rounded-md p-1.5 text-sm transition-colors",
            canNext
              ? "text-slate-600 hover:bg-slate-100"
              : "cursor-not-allowed text-slate-300"
          )}
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
