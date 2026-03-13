"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { customersApi } from "@/lib/api";
import { exportToCsv } from "@/lib/exportCsv";
import type { Customer, PaginatedResponse } from "@/types";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus, Download } from "lucide-react";
import dayjs from "dayjs";

export default function CustomersPage() {
  const router = useRouter();
  const [data, setData] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const [grade, setGrade] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (grade) params.grade = grade;

    customersApi
      .list(params)
      .then((res) => {
        const body = res.data as PaginatedResponse<Customer>;
        setData(body.data ?? []);
        setTotal(body.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, grade]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const columns: Column<Customer>[] = [
    { key: "customer_type", header: "유형" },
    { key: "name", header: "고객명" },
    { key: "phone_masked", header: "연락처" },
    { key: "email_masked", header: "이메일" },
    { key: "region", header: "지역" },
    {
      key: "grade",
      header: "등급",
      render: (row) => (
        <Badge status={row.grade}>
          {row.grade === "vip" ? "VIP" : row.grade === "repeat" ? "단골" : "일반"}
        </Badge>
      ),
    },
    {
      key: "created_at",
      header: "등록일",
      render: (row) => dayjs(row.created_at).format("YYYY-MM-DD"),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">고객 관리</h2>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() =>
              exportToCsv(
                "고객목록",
                ["유형", "고객명", "연락처", "이메일", "지역", "등급", "등록일"],
                data.map((r) => [
                  r.customer_type,
                  r.name,
                  r.phone_masked ?? "",
                  r.email_masked ?? "",
                  r.region ?? "",
                  r.grade,
                  dayjs(r.created_at).format("YYYY-MM-DD"),
                ])
              )
            }
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          <Link href="/arki/customers/new">
            <Button size="sm">
              <Plus className="h-4 w-4" />
              고객 등록
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Select
          options={[
            { value: "normal", label: "일반" },
            { value: "repeat", label: "단골" },
            { value: "vip", label: "VIP" },
          ]}
          placeholder="등급 전체"
          value={grade}
          onChange={(e) => {
            setGrade(e.target.value);
            setPage(1);
          }}
          className="w-32"
        />
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <>
          <Table
            columns={columns}
            data={data as unknown as Record<string, unknown>[]}
            onRowClick={(row) => router.push(`/arki/customers/${row.id}`)}
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
