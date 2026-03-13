"use client";

import { useEffect, useState, useCallback } from "react";
import { capacitySlotsApi } from "@/lib/api";
import type { CapacitySlot, PaginatedResponse } from "@/types";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { cn } from "@/lib/cn";

export default function CapacitySlotsPage() {
  const [data, setData] = useState<CapacitySlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 30;

  const [slotDate, setSlotDate] = useState("");
  const [team, setTeam] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (slotDate) params.slot_date = slotDate;
    if (team) params.delivery_team = team;

    capacitySlotsApi
      .list(params)
      .then((res) => {
        const body = res.data as PaginatedResponse<CapacitySlot>;
        setData(body.data ?? []);
        setTotal(body.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, slotDate, team]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const slotStatusLabels: Record<string, string> = {
    open: "여유",
    limited: "제한",
    full: "마감",
    closed: "종료",
  };

  const columns: Column<CapacitySlot>[] = [
    { key: "slot_date", header: "날짜" },
    { key: "delivery_team", header: "배송팀" },
    { key: "time_slot", header: "시간대" },
    {
      key: "max_capacity",
      header: "최대",
      render: (row) => `${row.max_capacity}`,
    },
    {
      key: "used_capacity",
      header: "사용",
      render: (row) => (
        <span
          className={cn(
            "font-medium",
            row.used_capacity >= row.max_capacity
              ? "text-red-600"
              : row.used_capacity >= row.max_capacity * 0.8
                ? "text-amber-600"
                : "text-slate-700"
          )}
        >
          {row.used_capacity}
        </span>
      ),
    },
    {
      key: "remaining_capacity",
      header: "잔여",
      render: (row) => (
        <span
          className={cn(
            "font-bold",
            row.remaining_capacity === 0
              ? "text-red-600"
              : row.remaining_capacity <= 2
                ? "text-amber-600"
                : "text-emerald-600"
          )}
        >
          {row.remaining_capacity}
        </span>
      ),
    },
    {
      key: "slot_status",
      header: "상태",
      render: (row) => (
        <Badge status={row.slot_status}>
          {slotStatusLabels[row.slot_status] ?? row.slot_status}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-slate-900">배송 CAPA</h2>

      <div className="flex flex-wrap gap-3">
        <Input
          type="date"
          value={slotDate}
          onChange={(e) => {
            setSlotDate(e.target.value);
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
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <>
          <Table columns={columns} data={data as unknown as Record<string, unknown>[]} />
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
