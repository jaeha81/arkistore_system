"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Edit2, X, Check } from "lucide-react";
import { productsApi } from "@/lib/api";
import type { Product } from "@/types";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    product_name: "",
    unit_price: "",
    option_text: "",
    supplier_name: "",
  });

  useEffect(() => {
    productsApi
      .get(id)
      .then((res) => {
        const data: Product = res.data?.data ?? res.data;
        setProduct(data);
        setForm({
          product_name: data.product_name,
          unit_price: String(data.unit_price),
          option_text: data.option_text ?? "",
          supplier_name: data.supplier_name ?? "",
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!product) return;
    setSaving(true);
    try {
      await productsApi.update(id, {
        product_name: form.product_name,
        unit_price: Number(form.unit_price),
        option_text: form.option_text || null,
        supplier_name: form.supplier_name || null,
      });
      setProduct((prev) =>
        prev
          ? {
              ...prev,
              product_name: form.product_name,
              unit_price: Number(form.unit_price),
              option_text: form.option_text || null,
              supplier_name: form.supplier_name || null,
            }
          : prev
      );
      setEditing(false);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="상품 정보 로딩 중..." />;
  if (!product) {
    return (
      <div className="py-16 text-center text-slate-400">
        상품 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/products")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        상품 목록으로
      </button>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="text-xl font-bold text-slate-900">{product.product_name}</h2>
          <Badge variant={product.is_active ? "green" : "gray"}>
            {product.is_active ? "활성" : "비활성"}
          </Badge>
        </div>
        {!editing && (
          <Button size="sm" variant="secondary" onClick={() => setEditing(true)}>
            <Edit2 className="h-4 w-4" />
            편집
          </Button>
        )}
      </div>

      {editing ? (
        <form
          onSubmit={handleSave}
          className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200 space-y-4"
        >
          <h3 className="font-semibold text-slate-900">상품 정보 편집</h3>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="상품명"
              value={form.product_name}
              onChange={(e) => setForm((p) => ({ ...p, product_name: e.target.value }))}
              required
            />
            <Input
              label="단가"
              type="number"
              value={form.unit_price}
              onChange={(e) => setForm((p) => ({ ...p, unit_price: e.target.value }))}
              required
            />
            <Input
              label="옵션"
              value={form.option_text}
              onChange={(e) => setForm((p) => ({ ...p, option_text: e.target.value }))}
              placeholder="선택사항"
            />
            <Input
              label="공급업체"
              value={form.supplier_name}
              onChange={(e) => setForm((p) => ({ ...p, supplier_name: e.target.value }))}
              placeholder="선택사항"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => setEditing(false)}
            >
              <X className="h-4 w-4" />
              취소
            </Button>
            <Button type="submit" size="sm" loading={saving}>
              <Check className="h-4 w-4" />
              저장
            </Button>
          </div>
        </form>
      ) : (
        <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h3 className="mb-4 font-semibold text-slate-900">상품 정보</h3>
          <dl className="grid grid-cols-2 gap-4">
            {[
              { label: "상품코드", value: product.product_code },
              { label: "상품명", value: product.product_name },
              { label: "브랜드", value: product.brand_name },
              { label: "카테고리", value: product.category_name ?? "—" },
              { label: "옵션", value: product.option_text ?? "—" },
              { label: "단가", value: `${Number(product.unit_price).toLocaleString()}원` },
              { label: "통화", value: product.currency },
              { label: "공급업체", value: product.supplier_name ?? "—" },
              { label: "등록일", value: dayjs(product.created_at).format("YYYY-MM-DD HH:mm") },
              { label: "수정일", value: dayjs(product.updated_at).format("YYYY-MM-DD HH:mm") },
            ].map((f) => (
              <div key={f.label}>
                <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">{f.label}</dt>
                <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}
