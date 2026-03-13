"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { happyCallsApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import dayjs from "dayjs";

export default function NewHappyCallPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    delivery_id: "",
    call_date: dayjs().format("YYYY-MM-DD"),
    caller_name: "",
    call_result: "satisfied",
    satisfaction_score: "5",
    notes: "",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await happyCallsApi.create({
        ...form,
        satisfaction_score: Number(form.satisfaction_score),
      });
      router.push("/arki/happy-calls");
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
      <h2 className="text-lg font-bold text-slate-900">해피콜 등록</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <Input
          label="배송 ID"
          value={form.delivery_id}
          onChange={(e) => update("delivery_id", e.target.value)}
          required
          placeholder="배송 ID 입력"
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="통화일"
            type="date"
            value={form.call_date}
            onChange={(e) => update("call_date", e.target.value)}
            required
          />
          <Input
            label="담당자"
            value={form.caller_name}
            onChange={(e) => update("caller_name", e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="결과"
            options={[
              { value: "satisfied", label: "만족" },
              { value: "neutral", label: "보통" },
              { value: "unsatisfied", label: "불만족" },
              { value: "no_answer", label: "부재" },
            ]}
            value={form.call_result}
            onChange={(e) => update("call_result", e.target.value)}
          />
          <Input
            label="만족도 (1~5)"
            type="number"
            min={1}
            max={5}
            value={form.satisfaction_score}
            onChange={(e) => update("satisfaction_score", e.target.value)}
          />
        </div>

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
            등록
          </Button>
        </div>
      </form>
    </div>
  );
}
