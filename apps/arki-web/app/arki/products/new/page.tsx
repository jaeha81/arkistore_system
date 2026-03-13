"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { productsApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";

export default function NewProductPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    product_code: "",
    product_name: "",
    brand_name: "",
    category_name: "",
    option_text: "",
    unit_price: "",
    currency: "KRW",
    supplier_name: "",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await productsApi.create({
        ...form,
        unit_price: Number(form.unit_price),
      });
      router.push("/arki/products");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: { message?: string } } } })
          ?.response?.data?.error?.message ?? "등록에 실패했습니다.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="text-lg font-bold text-slate-900">상품 등록</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="상품코드"
            value={form.product_code}
            onChange={(e) => update("product_code", e.target.value)}
            required
          />
          <Input
            label="상품명"
            value={form.product_name}
            onChange={(e) => update("product_name", e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="브랜드"
            value={form.brand_name}
            onChange={(e) => update("brand_name", e.target.value)}
            required
          />
          <Select
            label="카테고리"
            options={[
              { value: "가구", label: "가구" },
              { value: "가전", label: "가전" },
              { value: "생활", label: "생활" },
              { value: "인테리어", label: "인테리어" },
            ]}
            placeholder="선택"
            value={form.category_name}
            onChange={(e) => update("category_name", e.target.value)}
          />
        </div>

        <Input
          label="옵션"
          value={form.option_text}
          onChange={(e) => update("option_text", e.target.value)}
          placeholder="예: 색상, 사이즈"
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="단가"
            type="number"
            value={form.unit_price}
            onChange={(e) => update("unit_price", e.target.value)}
            required
          />
          <Input
            label="공급업체"
            value={form.supplier_name}
            onChange={(e) => update("supplier_name", e.target.value)}
          />
        </div>

        {error && (
          <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="secondary"
            onClick={() => router.back()}
          >
            취소
          </Button>
          <Button type="submit" loading={loading}>
            등록
          </Button>
        </div>
      </form>
    </div>
  );
}
