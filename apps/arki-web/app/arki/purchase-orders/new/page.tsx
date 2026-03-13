"use client";

import { useState, useMemo, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { purchaseOrdersApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import dayjs from "dayjs";

export default function NewPurchaseOrderPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);

  const [form, setForm] = useState({
    supplier: "",
    order_date: dayjs().format("YYYY-MM-DD"),
    expected_delivery_date: "",
    total_amount: "",
    notes: "",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await purchaseOrdersApi.create(
        {
          ...form,
          total_amount: Number(form.total_amount),
        },
        idempotencyKey
      );
      router.push("/arki/purchase-orders");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: { message?: string } } } })
          ?.response?.data?.error?.message ?? "생성에 실패했습니다.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="text-lg font-bold text-slate-900">발주서 생성</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <Input
          label="공급업체"
          value={form.supplier}
          onChange={(e) => update("supplier", e.target.value)}
          required
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="발주일"
            type="date"
            value={form.order_date}
            onChange={(e) => update("order_date", e.target.value)}
            required
          />
          <Input
            label="입고예정일"
            type="date"
            value={form.expected_delivery_date}
            onChange={(e) => update("expected_delivery_date", e.target.value)}
          />
        </div>

        <Input
          label="총 금액"
          type="number"
          value={form.total_amount}
          onChange={(e) => update("total_amount", e.target.value)}
          required
        />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            비고
          </label>
          <textarea
            className="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            rows={3}
            value={form.notes}
            onChange={(e) => update("notes", e.target.value)}
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
            생성
          </Button>
        </div>
      </form>
    </div>
  );
}
