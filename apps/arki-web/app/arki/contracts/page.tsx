"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { contractsApi } from "@/lib/api";
import { exportToCsv } from "@/lib/exportCsv";
import type { Contract, PaginatedResponse } from "@/types";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus, Download } from "lucide-react";
import dayjs from "dayjs";

export default function ContractsPage() {
  const router = useRouter();
  const [data, setData] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;
  const [status, setStatus] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (status) params.contract_status = status;

    contractsApi
      .list(params)
      .then((res) => {
        const body = res.data as PaginatedResponse<Contract>;
        setData(body.data ?? []);
        setTotal(body.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, status]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const statusLabels: Record<string, string> = {
    draft: "초안",
    signed: "서명완료",
    confirmed: "확정",
    cancelled: "취소",
  };

  const columns: Column<Contract>[] = [
    { key: "contract_number", header: "계약번호" },
    { key: "customer_id", header: "고객" },
    {
      key: "contract_status",
      header: "상태",
      render: (row) => (
        <Badge status={row.contract_status}>
          {statusLabels[row.contract_status] ?? row.contract_status}
        </Badge>
      ),
    },
    {
      key: "contract_date",
      header: "계약일",
      render: (row) => dayjs(row.contract_date).format("YYYY-MM-DD"),
    },
    {
      key: "contract_amount",
      header: "계약금액",
      render: (row) => `${Number(row.contract_amount).toLocaleString()}원`,
    },
    {
      key: "delivery_required",
      header: "배송",
      render: (row) => (
        <Badge variant={row.delivery_required ? "blue" : "gray"}>
          {row.delivery_required ? "필요" : "불필요"}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">계약 관리</h2>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() =>
              exportToCsv(
                "계약목록",
                ["계약번호", "계약일", "계약금액", "계약금", "상태", "배송필요"],
                data.map((r) => [
                  r.contract_number ?? "",
                  dayjs(r.contract_date).format("YYYY-MM-DD"),
                  r.contract_amount,
                  r.deposit_amount ?? "",
                  statusLabels[r.contract_status] ?? r.contract_status,
                  r.delivery_required ? "필요" : "불필요",
                ])
              )
            }
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          <Link href="/arki/contracts/new">
            <Button size="sm">
              <Plus className="h-4 w-4" />
              계약 생성
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Select
          options={[
            { value: "draft", label: "초안" },
            { value: "signed", label: "서명완료" },
            { value: "confirmed", label: "확정" },
            { value: "cancelled", label: "취소" },
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
            onRowClick={(row) => router.push(`/arki/contracts/${row.id}`)}
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
