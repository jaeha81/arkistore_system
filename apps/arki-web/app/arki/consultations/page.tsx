"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { consultationsApi } from "@/lib/api";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus } from "lucide-react";
import dayjs from "dayjs";

interface Consultation {
  id: string;
  consultation_number: string;
  customer_name: string;
  product_name: string;
  consultation_status: string;
  consultation_date: string;
  sales_rep: string;
  [key: string]: unknown;
}

export default function ConsultationsPage() {
  const router = useRouter();
  const [data, setData] = useState<Consultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const fetchData = useCallback(() => {
    setLoading(true);
    consultationsApi
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

  const statusLabels: Record<string, string> = {
    scheduled: "예약",
    in_progress: "진행중",
    completed: "완료",
    cancelled: "취소",
  };

  const columns: Column<Consultation>[] = [
    { key: "consultation_number", header: "상담번호" },
    { key: "customer_name", header: "고객명" },
    { key: "product_name", header: "상품명" },
    {
      key: "consultation_status",
      header: "상태",
      render: (row) => (
        <Badge status={row.consultation_status}>
          {statusLabels[row.consultation_status] ?? row.consultation_status}
        </Badge>
      ),
    },
    {
      key: "consultation_date",
      header: "상담일",
      render: (row) => dayjs(row.consultation_date).format("YYYY-MM-DD"),
    },
    { key: "sales_rep", header: "담당자" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">상담 관리</h2>
        <Link href="/arki/consultations/new">
          <Button size="sm">
            <Plus className="h-4 w-4" />
            상담 등록
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
            onRowClick={(row) => router.push(`/arki/consultations/${row.id}`)}
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
