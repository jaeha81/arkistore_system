"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { leadsApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";

export default function NewLeadPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    company_name: "",
    contact_name: "",
    contact_phone: "",
    contact_email: "",
    lead_source: "",
    notes: "",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await leadsApi.create(form);
      router.push("/arki/leads");
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
      <h2 className="text-lg font-bold text-slate-900">리드 등록</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="회사명"
            value={form.company_name}
            onChange={(e) => update("company_name", e.target.value)}
            required
          />
          <Input
            label="담당자명"
            value={form.contact_name}
            onChange={(e) => update("contact_name", e.target.value)}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="연락처"
            type="tel"
            value={form.contact_phone}
            onChange={(e) => update("contact_phone", e.target.value)}
          />
          <Input
            label="이메일"
            type="email"
            value={form.contact_email}
            onChange={(e) => update("contact_email", e.target.value)}
          />
        </div>

        <Select
          label="유입경로"
          options={[
            { value: "website", label: "웹사이트" },
            { value: "phone", label: "전화문의" },
            { value: "referral", label: "소개" },
            { value: "exhibition", label: "전시회" },
            { value: "sns", label: "SNS" },
            { value: "other", label: "기타" },
          ]}
          placeholder="선택"
          value={form.lead_source}
          onChange={(e) => update("lead_source", e.target.value)}
        />

        <div>
          <label className="mb-1.5 block text-sm font-medium text-slate-700">
            메모
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
