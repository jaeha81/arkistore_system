"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { invoicesApi } from "@/lib/api";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import dayjs from "dayjs";

interface Invoice {
  id: string;
  invoice_number: string;
  supplier: string;
  invoice_date: string;
  total_amount: number;
  payment_status: string;
  [key: string]: unknown;
}

export default function InvoicesPage() {
  const router = useRouter();
  const [data, setData] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const fetchData = useCallback(() => {
    setLoading(true);
    invoicesApi
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

  const paymentLabels: Record<string, string> = {
    unpaid: "미결제",
    partially_paid: "부분결제",
    paid: "결제완료",
  };

  const columns: Column<Invoice>[] = [
    { key: "invoice_number", header: "인보이스번호" },
    { key: "supplier", header: "공급업체" },
    {
      key: "invoice_date",
      header: "인보이스일",
      render: (row) => dayjs(row.invoice_date).format("YYYY-MM-DD"),
    },
    {
      key: "total_amount",
      header: "금액",
      render: (row) => `${Number(row.total_amount).toLocaleString()}`,
    },
    {
      key: "payment_status",
      header: "결제상태",
      render: (row) => (
        <Badge status={row.payment_status}>
          {paymentLabels[row.payment_status] ?? row.payment_status}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-slate-900">인보이스</h2>

      {loading ? (
        <Spinner />
      ) : (
        <>
          <Table
            columns={columns}
            data={data as unknown as Record<string, unknown>[]}
            onRowClick={(row) => router.push(`/arki/invoices/${row.id}`)}
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
