import { cn } from "../../lib/utils";
import { Loader2 } from "lucide-react";

interface SpinnerProps {
  className?: string;
  size?: "sm" | "md" | "lg";
  text?: string;
}

const sizeMap = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-10 w-10",
};

export default function Spinner({
  className,
  size = "md",
  text,
}: SpinnerProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-2 py-12 text-gray-400",
        className
      )}
    >
      <Loader2 className={cn("animate-spin", sizeMap[size])} />
      {text && <p className="text-sm">{text}</p>}
    </div>
  );
}
