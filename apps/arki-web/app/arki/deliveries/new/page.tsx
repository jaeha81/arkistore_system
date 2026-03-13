"use client";

import { useState, useMemo, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { deliveriesApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import dayjs from "dayjs";

export default function NewDeliveryPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);

  const [form, setForm] = useState({
    contract_id: "",
    delivery_date: dayjs().add(1, "day").format("YYYY-MM-DD"),
    time_slot: "오전",
    delivery_team: "",
    vehicle_code: "",
    address_text: "",
    ladder_required: false,
    memo: "",
  });

  const updateField = (field: string, value: string | boolean) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await deliveriesApi.create(form, idempotencyKey);
      router.push("/arki/deliveries");
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
      <h2 className="text-lg font-bold text-slate-900">배송 예약</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <Input
          label="계약 ID"
          value={form.contract_id}
          onChange={(e) => updateField("contract_id", e.target.value)}
          required
          placeholder="계약 ID 입력"
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="배송일"
            type="date"
            value={form.delivery_date}
            onChange={(e) => updateField("delivery_date", e.target.value)}
            required
          />
          <Select
            label="시간대"
            options={[
              { value: "오전", label: "오전" },
              { value: "오후", label: "오후" },
            ]}
            value={form.time_slot}
            onChange={(e) => updateField("time_slot", e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="배송팀"
            options={[
              { value: "A팀", label: "A팀" },
              { value: "B팀", label: "B팀" },
              { value: "C팀", label: "C팀" },
            ]}
            placeholder="선택"
            value={form.delivery_team}
            onChange={(e) => updateField("delivery_team", e.target.value)}
            required
          />
          <Input
            label="차량코드"
            value={form.vehicle_code}
            onChange={(e) => updateField("vehicle_code", e.target.value)}
            placeholder="예: V001"
          />
        </div>

        <Input
          label="배송지 주소"
          value={form.address_text}
          onChange={(e) => updateField("address_text", e.target.value)}
          required
        />

        <div className="flex items-center gap-2">
          <input
            id="ladder_required"
            type="checkbox"
            checked={form.ladder_required}
            onChange={(e) => updateField("ladder_required", e.target.checked)}
            className="h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-500"
          />
          <label
            htmlFor="ladder_required"
            className="text-sm font-medium text-slate-700"
          >
            사다리차 필요
          </label>
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            메모
          </label>
          <textarea
            className="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-500"
            rows={3}
            value={form.memo}
            onChange={(e) => updateField("memo", e.target.value)}
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
            배송 예약
          </Button>
        </div>
      </form>
    </div>
  );
}
