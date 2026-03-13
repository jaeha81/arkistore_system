"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { leadsApi } from "@/lib/api";
import { exportToCsv } from "@/lib/exportCsv";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus, Download } from "lucide-react";
import dayjs from "dayjs";

interface Lead {
  id: string;
  lead_number: string;
  company_name: string;
  contact_name: string;
  lead_source: string;
  lead_status: string;
  created_at: string;
  [key: string]: unknown;
}

export default function LeadsPage() {
  const router = useRouter();
  const [data, setData] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;
  const [status, setStatus] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (status) params.lead_status = status;

    leadsApi
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
    new: "신규",
    in_progress: "진행중",
    converted: "전환",
    closed: "종료",
    dropped: "이탈",
  };

  const columns: Column<Lead>[] = [
    { key: "lead_number", header: "리드번호" },
    { key: "company_name", header: "회사명" },
    { key: "contact_name", header: "담당자" },
    { key: "lead_source", header: "유입경로" },
    {
      key: "lead_status",
      header: "상태",
      render: (row) => (
        <Badge status={row.lead_status}>
          {statusLabels[row.lead_status] ?? row.lead_status}
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
        <h2 className="text-lg font-bold text-slate-900">문의 / 리드</h2>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() =>
              exportToCsv(
                data.map((row) => ({
                  리드번호: row.lead_number,
                  회사명: row.company_name,
                  담당자: row.contact_name,
                  유입경로: row.lead_source,
                  상태: statusLabels[row.lead_status] ?? row.lead_status,
                  등록일: dayjs(row.created_at).format("YYYY-MM-DD"),
                })),
                "leads"
              )
            }
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          <Link href="/arki/leads/new">
            <Button size="sm">
              <Plus className="h-4 w-4" />
              리드 등록
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Select
          options={[
            { value: "new", label: "신규" },
            { value: "in_progress", label: "진행중" },
            { value: "converted", label: "전환" },
            { value: "closed", label: "종료" },
            { value: "dropped", label: "이탈" },
          ]}
          placeholder="상태 전체"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
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
            onRowClick={(row) => router.push(`/arki/leads/${row.id}`)}
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
