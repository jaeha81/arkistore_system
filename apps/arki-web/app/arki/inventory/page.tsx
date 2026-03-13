"use client";

import { useEffect, useState, useCallback } from "react";
import { inventoryApi } from "@/lib/api";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";

interface InventoryItem {
  id: string;
  product_name: string;
  product_code: string;
  warehouse: string;
  quantity: number;
  unit: string;
  min_stock: number;
  inventory_status: string;
  [key: string]: unknown;
}

export default function InventoryPage() {
  const [data, setData] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const fetchData = useCallback(() => {
    setLoading(true);
    inventoryApi
      .list({ page, page_size: pageSize })
      .then((res) => {
        const body = res.data;
        setData(body.data ?? []);
        setTotal(body.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const columns: Column<InventoryItem>[] = [
    { key: "product_code", header: "상품코드" },
    { key: "product_name", header: "상품명" },
    { key: "warehouse", header: "창고" },
    {
      key: "quantity",
      header: "수량",
      render: (row) => `${row.quantity} ${row.unit ?? "EA"}`,
    },
    {
      key: "inventory_status",
      header: "재고상태",
      render: (row) => {
        const status = row.inventory_status ?? (row.quantity < (row.min_stock ?? 10) ? "low_stock" : "normal");
        const label =
          status === "low_stock"
            ? "재고부족"
            : status === "out_of_stock"
              ? "품절"
              : status === "normal"
                ? "정상"
                : String(status);
        return (
          <Badge status={String(status)}>{label}</Badge>
        );
      },
    },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-slate-900">재고 현황</h2>

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
