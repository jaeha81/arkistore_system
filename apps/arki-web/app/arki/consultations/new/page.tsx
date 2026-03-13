"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { consultationsApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import dayjs from "dayjs";

export default function NewConsultationPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    customer_id: "",
    product_id: "",
    consultation_date: dayjs().format("YYYY-MM-DD"),
    consultation_type: "visit",
    sales_rep: "",
    notes: "",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await consultationsApi.create(form);
      router.push("/arki/consultations");
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
      <h2 className="text-lg font-bold text-slate-900">상담 등록</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="고객 ID"
            value={form.customer_id}
            onChange={(e) => update("customer_id", e.target.value)}
            required
            placeholder="고객 ID 입력"
          />
          <Input
            label="상품 ID"
            value={form.product_id}
            onChange={(e) => update("product_id", e.target.value)}
            placeholder="상품 ID 입력"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="상담일"
            type="date"
            value={form.consultation_date}
            onChange={(e) => update("consultation_date", e.target.value)}
            required
          />
          <Select
            label="상담유형"
            options={[
              { value: "visit", label: "방문" },
              { value: "phone", label: "전화" },
              { value: "online", label: "온라인" },
            ]}
            value={form.consultation_type}
            onChange={(e) => update("consultation_type", e.target.value)}
          />
        </div>

        <Input
          label="담당자"
          value={form.sales_rep}
          onChange={(e) => update("sales_rep", e.target.value)}
          required
        />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            상담 내용
          </label>
          <textarea
            className="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            rows={4}
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
            등록
          </Button>
        </div>
      </form>
    </div>
  );
}
