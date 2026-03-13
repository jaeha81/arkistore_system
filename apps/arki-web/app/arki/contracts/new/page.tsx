"use client";

import { useState, useMemo, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { contractsApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import dayjs from "dayjs";

export default function NewContractPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);

  const [form, setForm] = useState({
    customer_id: "",
    contract_date: dayjs().format("YYYY-MM-DD"),
    contract_amount: "",
    deposit_amount: "",
    delivery_required: "true",
    remarks: "",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await contractsApi.create(
        {
          ...form,
          contract_amount: Number(form.contract_amount),
          deposit_amount: form.deposit_amount
            ? Number(form.deposit_amount)
            : null,
          delivery_required: form.delivery_required === "true",
        },
        idempotencyKey
      );
      router.push("/arki/contracts");
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
      <h2 className="text-lg font-bold text-slate-900">계약 생성</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <Input
          label="고객 ID"
          value={form.customer_id}
          onChange={(e) => update("customer_id", e.target.value)}
          required
          placeholder="고객 ID 입력"
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="계약일"
            type="date"
            value={form.contract_date}
            onChange={(e) => update("contract_date", e.target.value)}
            required
          />
          <Select
            label="배송 필요"
            options={[
              { value: "true", label: "필요" },
              { value: "false", label: "불필요" },
            ]}
            value={form.delivery_required}
            onChange={(e) => update("delivery_required", e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="계약금액"
            type="number"
            value={form.contract_amount}
            onChange={(e) => update("contract_amount", e.target.value)}
            required
          />
          <Input
            label="계약금"
            type="number"
            value={form.deposit_amount}
            onChange={(e) => update("deposit_amount", e.target.value)}
            placeholder="선택사항"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            비고
          </label>
          <textarea
            className="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            rows={3}
            value={form.remarks}
            onChange={(e) => update("remarks", e.target.value)}
          />
        </div>

        <p className="text-xs text-slate-400">
          Idempotency-Key: {idempotencyKey}
        </p>

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
            계약 생성
          </Button>
        </div>
      </form>
    </div>
  );
}
