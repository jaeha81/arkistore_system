"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { purchaseRequestsApi } from "@/lib/api";
import { exportToCsv } from "@/lib/exportCsv";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus, Download } from "lucide-react";
import dayjs from "dayjs";

interface PurchaseRequest {
  id: string;
  pr_number: string;
  request_date: string;
  requester: string;
  pr_status: string;
  total_items: number;
  notes: string;
  [key: string]: unknown;
}

export default function PurchaseRequestsPage() {
  const router = useRouter();
  const [data, setData] = useState<PurchaseRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;
  const [status, setStatus] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (status) params.pr_status = status;

    purchaseRequestsApi
      .list(params)
      .then((res) => {
        setData(res.data?.data ?? []);
        setTotal(res.data?.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, status]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const statusLabels: Record<string, string> = {
    requested: "요청",
    reviewed: "검토",
    approved: "승인",
    rejected: "반려",
    converted_to_order: "발주전환",
  };

  const columns: Column<PurchaseRequest>[] = [
    { key: "pr_number", header: "요청번호" },
    {
      key: "request_date",
      header: "요청일",
      render: (row) => dayjs(row.request_date).format("YYYY-MM-DD"),
    },
    { key: "requester", header: "요청자" },
    {
      key: "pr_status",
      header: "상태",
      render: (row) => (
        <Badge status={row.pr_status}>
          {statusLabels[row.pr_status] ?? row.pr_status}
        </Badge>
      ),
    },
    {
      key: "total_items",
      header: "품목수",
      render: (row) => `${row.total_items ?? 0}건`,
    },
    { key: "notes", header: "비고" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">발주 요청</h2>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() =>
              exportToCsv(
                "발주요청목록",
                ["요청번호", "요청일", "요청자", "상태", "품목수", "비고"],
                data.map((r) => [
                  r.pr_number,
                  dayjs(r.request_date).format("YYYY-MM-DD"),
                  r.requester,
                  statusLabels[r.pr_status] ?? r.pr_status,
                  r.total_items ?? 0,
                  r.notes ?? "",
                ])
              )
            }
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          <Link href="/arki/purchase-requests/new">
            <Button size="sm">
              <Plus className="h-4 w-4" />
              발주 요청 등록
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Select
          options={[
            { value: "requested", label: "요청" },
            { value: "reviewed", label: "검토" },
            { value: "approved", label: "승인" },
            { value: "rejected", label: "반려" },
            { value: "converted_to_order", label: "발주전환" },
          ]}
          placeholder="상태 전체"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
          className="w-36"
        />
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <>
          <Table
            columns={columns}
            data={data as unknown as Record<string, unknown>[]}
            onRowClick={(row) => router.push(`/arki/purchase-requests/${row.id}`)}
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
