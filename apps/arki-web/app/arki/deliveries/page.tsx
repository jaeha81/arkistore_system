"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { deliveriesApi } from "@/lib/api";
import { exportToCsv } from "@/lib/exportCsv";
import type { Delivery, PaginatedResponse } from "@/types";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus, Download } from "lucide-react";

export default function DeliveriesPage() {
  const router = useRouter();
  const [data, setData] = useState<Delivery[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const [deliveryDate, setDeliveryDate] = useState("");
  const [team, setTeam] = useState("");
  const [status, setStatus] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (deliveryDate) params.delivery_date = deliveryDate;
    if (team) params.delivery_team = team;
    if (status) params.delivery_status = status;

    deliveriesApi
      .list(params)
      .then((res) => {
        const body = res.data as PaginatedResponse<Delivery>;
        setData(body.data ?? []);
        setTotal(body.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, deliveryDate, team, status]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const statusLabels: Record<string, string> = {
    scheduled: "예약",
    confirmed: "확정",
    in_transit: "배송중",
    completed: "완료",
    delayed: "지연",
    cancelled: "취소",
  };

  const columns: Column<Delivery>[] = [
    { key: "delivery_number", header: "배송번호" },
    { key: "delivery_date", header: "배송일" },
    { key: "time_slot", header: "시간대" },
    { key: "delivery_team", header: "배송팀" },
    { key: "address_text", header: "배송지" },
    {
      key: "delivery_status",
      header: "상태",
      render: (row) => (
        <Badge status={row.delivery_status}>
          {statusLabels[row.delivery_status] ?? row.delivery_status}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">배송 관리</h2>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={() =>
              exportToCsv(
                "배송목록",
                ["배송번호", "배송일", "시간대", "배송팀", "배송지", "상태"],
                data.map((r) => [
                  r.delivery_number ?? "",
                  r.delivery_date,
                  r.time_slot,
                  r.delivery_team,
                  r.address_text,
                  statusLabels[r.delivery_status] ?? r.delivery_status,
                ])
              )
            }
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          <Link href="/arki/deliveries/new">
            <Button size="sm">
              <Plus className="h-4 w-4" />
              배송 예약
            </Button>
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Input
          type="date"
          value={deliveryDate}
          onChange={(e) => {
            setDeliveryDate(e.target.value);
            setPage(1);
          }}
          className="w-40"
        />
        <Select
          options={[
            { value: "A팀", label: "A팀" },
            { value: "B팀", label: "B팀" },
            { value: "C팀", label: "C팀" },
          ]}
          placeholder="팀 전체"
          value={team}
          onChange={(e) => {
            setTeam(e.target.value);
            setPage(1);
          }}
          className="w-28"
        />
        <Select
          options={[
            { value: "scheduled", label: "예약" },
            { value: "confirmed", label: "확정" },
            { value: "in_transit", label: "배송중" },
            { value: "completed", label: "완료" },
            { value: "delayed", label: "지연" },
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
            onRowClick={(row) => router.push(`/arki/deliveries/${row.id}`)}
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
