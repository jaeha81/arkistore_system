"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { happyCallsApi } from "@/lib/api";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus } from "lucide-react";
import dayjs from "dayjs";

interface HappyCall {
  id: string;
  delivery_id: string;
  call_date: string;
  caller_name: string;
  call_result: string;
  satisfaction_score: number;
  notes: string;
  [key: string]: unknown;
}

export default function HappyCallsPage() {
  const router = useRouter();
  const [data, setData] = useState<HappyCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const fetchData = useCallback(() => {
    setLoading(true);
    happyCallsApi
      .list({ page, page_size: pageSize })
      .then((res) => {
        setData(res.data?.data ?? []);
        setTotal(res.data?.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const resultLabels: Record<string, string> = {
    satisfied: "만족",
    neutral: "보통",
    unsatisfied: "불만족",
    no_answer: "부재",
  };

  const columns: Column<HappyCall>[] = [
    {
      key: "delivery_id",
      header: "배송 ID",
      render: (row) => row.delivery_id?.slice(0, 8) ?? "—",
    },
    {
      key: "call_date",
      header: "통화일",
      render: (row) => dayjs(row.call_date).format("YYYY-MM-DD"),
    },
    { key: "caller_name", header: "담당자" },
    {
      key: "call_result",
      header: "결과",
      render: (row) => (
        <Badge
          status={
            row.call_result === "satisfied"
              ? "completed"
              : row.call_result === "unsatisfied"
                ? "cancelled"
                : row.call_result === "no_answer"
                  ? "inactive"
                  : "pending"
          }
        >
          {resultLabels[row.call_result] ?? row.call_result}
        </Badge>
      ),
    },
    {
      key: "satisfaction_score",
      header: "만족도",
      render: (row) => (
        <span className="font-medium">
          {row.satisfaction_score != null ? `${row.satisfaction_score}점` : "—"}
        </span>
      ),
    },
    { key: "notes", header: "비고" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">해피콜</h2>
        <Link href="/arki/happy-calls/new">
          <Button size="sm">
            <Plus className="h-4 w-4" />
            해피콜 등록
          </Button>
        </Link>
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <>
          <Table
            columns={columns}
            data={data as unknown as Record<string, unknown>[]}
            onRowClick={(row) => router.push(`/arki/happy-calls/${row.id}`)}
          />
          <Pagination
            page={page}
            pageSize={pageSize}
            total={total}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
