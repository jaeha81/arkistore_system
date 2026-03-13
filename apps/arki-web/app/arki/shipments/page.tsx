"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { shipmentsApi } from "@/lib/api";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import dayjs from "dayjs";

interface Shipment {
  id: string;
  bl_number: string;
  shipping_company: string;
  departure_date: string;
  estimated_arrival_date: string;
  customs_status: string;
  shipment_status: string;
  [key: string]: unknown;
}

export default function ShipmentsPage() {
  const router = useRouter();
  const [data, setData] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;
  const [customsStatus, setCustomsStatus] = useState("");
  const [shipmentStatus, setShipmentStatus] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (customsStatus) params.customs_status = customsStatus;
    if (shipmentStatus) params.shipment_status = shipmentStatus;

    shipmentsApi
      .list(params)
      .then((res) => {
        setData(res.data?.data ?? []);
        setTotal(res.data?.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, customsStatus, shipmentStatus]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const columns: Column<Shipment>[] = [
    { key: "bl_number", header: "BL번호" },
    { key: "shipping_company", header: "선사" },
    {
      key: "departure_date",
      header: "출발일",
      render: (row) =>
        row.departure_date
          ? dayjs(row.departure_date).format("YYYY-MM-DD")
          : "—",
    },
    {
      key: "estimated_arrival_date",
      header: "도착예정일",
      render: (row) =>
        row.estimated_arrival_date
          ? dayjs(row.estimated_arrival_date).format("YYYY-MM-DD")
          : "—",
    },
    {
      key: "customs_status",
      header: "통관상태",
      render: (row) => (
        <Badge status={row.customs_status}>
          {row.customs_status}
        </Badge>
      ),
    },
    {
      key: "shipment_status",
      header: "선적상태",
      render: (row) => (
        <Badge status={row.shipment_status}>
          {row.shipment_status}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-slate-900">BL / 선적 관리</h2>

      <div className="flex flex-wrap gap-3">
        <Select
          options={[
            { value: "pending", label: "대기" },
            { value: "in_progress", label: "진행중" },
            { value: "completed", label: "완료" },
            { value: "delayed", label: "지연" },
          ]}
          placeholder="통관상태 전체"
          value={customsStatus}
          onChange={(e) => {
            setCustomsStatus(e.target.value);
            setPage(1);
          }}
          className="w-40"
        />
        <Select
          options={[
            { value: "pending", label: "대기" },
            { value: "in_transit", label: "운송중" },
            { value: "arrived", label: "도착" },
            { value: "completed", label: "완료" },
          ]}
          placeholder="선적상태 전체"
          value={shipmentStatus}
          onChange={(e) => {
            setShipmentStatus(e.target.value);
            setPage(1);
          }}
          className="w-40"
        />
      </div>

      {loading ? (
        <Spinner />
      ) : (
        <>
          <Table
            columns={columns}
            data={data as unknown as Record<string, unknown>[]}
            onRowClick={(row) => router.push(`/arki/shipments/${row.id}`)}
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
