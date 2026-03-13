"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { purchaseOrdersApi } from "@/lib/api";
import { exportToCsv } from "@/lib/exportCsv";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus, Download } from "lucide-react";
import dayjs from "dayjs";

interface PurchaseOrder {
  id: string;
  po_number: string;
  supplier: string;
  order_date: string;
  po_status: string;
  total_amount: number;
  expected_delivery_date: string;
  [key: string]: unknown;
}

export default function PurchaseOrdersPage() {
  const router = useRouter();
  const [data, setData] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;
  const [status, setStatus] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (status) params.po_status = status;

    purchaseOrdersApi
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
    created: "생성",
    ordered: "발주",
    invoiced: "인보이스",
    shipped: "선적",
    completed: "완료",
    cancelled: "취소",
  };

  const columns: Column<PurchaseOrder>[] = [
    { key: "po_number", header: "발주번호" },
    { key: "supplier", header: "공급업체" },
    {
      key: "order_date",
      header: "발주일",
      render: (row) => dayjs(row.order_date).format("YYYY-MM-DD"),
    },
    {
      key: "po_status",
      header: "상태",
      render: (row) => (
        <Badge status={row.po_status}>
          {statusLabels[row.po_status] ?? row.po_status}
        </Badge>
      ),
    },
    {
      key: "total_amount",
      header: "금액",
      render: (row) => `${Number(row.total_amount).toLocaleString()}`,
    },
    {
      key: "expected_delivery_date",
      header: "입고예정일",
      render: (row) =>
        row.expected_delivery_date
          ? dayjs(row.expected_delivery_date).format("YYYY-MM-DD")
          : "—",
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">발주서 관리</h2>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() =>
              exportToCsv(
                data.map((row) => ({
                  발주번호: row.po_number,
                  공급업체: row.supplier,
                  발주일: row.order_date
                    ? dayjs(row.order_date).format("YYYY-MM-DD")
                    : "",
                  상태: statusLabels[row.po_status] ?? row.po_status,
                  금액: row.total_amount,
                  입고예정일: row.expected_delivery_date
                    ? dayjs(row.expected_delivery_date).format("YYYY-MM-DD")
                    : "",
                })),
                "purchase-orders"
              )
            }
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          <Link href="/arki/purchase-orders/new">
            <Button size="sm">
              <Plus className="h-4 w-4" />
              발주서 생성
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Select
          options={[
            { value: "created", label: "생성" },
            { value: "ordered", label: "발주" },
            { value: "invoiced", label: "인보이스" },
            { value: "shipped", label: "선적" },
            { value: "completed", label: "완료" },
            { value: "cancelled", label: "취소" },
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
            onRowClick={(row) => router.push(`/arki/purchase-orders/${row.id}`)}
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
