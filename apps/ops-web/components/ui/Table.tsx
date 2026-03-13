import { cn } from "../../lib/utils";

interface TableProps {
  children: React.ReactNode;
  className?: string;
}

export function Table({ children, className }: TableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table
        className={cn("min-w-full divide-y divide-gray-200", className)}
      >
        {children}
      </table>
    </div>
  );
}

export function Thead({ children, className }: TableProps) {
  return (
    <thead className={cn("bg-gray-50", className)}>{children}</thead>
  );
}

export function Tbody({ children, className }: TableProps) {
  return (
    <tbody
      className={cn("divide-y divide-gray-200 bg-white", className)}
    >
      {children}
    </tbody>
  );
}

export function Th({ children, className }: TableProps) {
  return (
    <th
      className={cn(
        "px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500",
        className
      )}
    >
      {children}
    </th>
  );
}

interface TdProps extends TableProps {
  onClick?: () => void;
}

export function Td({ children, className, onClick }: TdProps) {
  return (
    <td
      onClick={onClick}
      className={cn(
        "whitespace-nowrap px-4 py-3 text-sm text-gray-700",
        onClick && "cursor-pointer",
        className
      )}
    >
      {children}
    </td>
  );
}

export function Tr({
  children,
  className,
  onClick,
}: TdProps) {
  return (
    <tr
      onClick={onClick}
      className={cn(
        "transition-colors",
        onClick && "cursor-pointer hover:bg-gray-50",
        className
      )}
    >
      {children}
    </tr>
  );
}
