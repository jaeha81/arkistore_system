"use client";

import { cn } from "@/lib/cn";
import { Loader2 } from "lucide-react";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeMap = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
};

export default function Spinner({ size = "md", className }: SpinnerProps) {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2
        className={cn("animate-spin text-slate-400", sizeMap[size], className)}
      />
    </div>
  );
}
