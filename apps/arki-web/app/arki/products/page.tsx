"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { productsApi } from "@/lib/api";
import type { Product, PaginatedResponse } from "@/types";
import Table, { type Column } from "@/components/ui/Table";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import Pagination from "@/components/ui/Pagination";
import { Plus } from "lucide-react";

export default function ProductsPage() {
  const router = useRouter();
  const [data, setData] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const [category, setCategory] = useState("");
  const [isActive, setIsActive] = useState("");

  const fetchData = useCallback(() => {
    setLoading(true);
    const params: Record<string, unknown> = { page, page_size: pageSize };
    if (category) params.category = category;
    if (isActive) params.is_active = isActive === "true";

    productsApi
      .list(params)
      .then((res) => {
        const body = res.data as PaginatedResponse<Product>;
        setData(body.data ?? []);
        setTotal(body.meta?.total ?? 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, category, isActive]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const columns: Column<Product>[] = [
    { key: "product_code", header: "상품코드" },
    { key: "product_name", header: "상품명" },
    { key: "category_name", header: "카테고리" },
    { key: "brand_name", header: "브랜드" },
    {
      key: "unit_price",
      header: "단가",
      render: (row) => `${Number(row.unit_price).toLocaleString()}원`,
    },
    {
      key: "is_active",
      header: "상태",
      render: (row) => (
        <Badge variant={row.is_active ? "green" : "gray"}>
          {row.is_active ? "활성" : "비활성"}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">상품 마스터</h2>
        <Link href="/arki/products/new">
          <Button size="sm">
            <Plus className="h-4 w-4" />
            상품 등록
          </Button>
        </Link>
      </div>

      <div className="flex flex-wrap gap-3">
        <Select
          options={[
            { value: "가구", label: "가구" },
            { value: "가전", label: "가전" },
            { value: "생활", label: "생활" },
            { value: "인테리어", label: "인테리어" },
          ]}
          placeholder="카테고리 전체"
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setPage(1);
          }}
          className="w-40"
        />
        <Select
          options={[
            { value: "true", label: "활성" },
            { value: "false", label: "비활성" },
          ]}
          placeholder="상태 전체"
          value={isActive}
          onChange={(e) => {
            setIsActive(e.target.value);
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
            onRowClick={(row) => router.push(`/arki/products/${row.id}`)}
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
