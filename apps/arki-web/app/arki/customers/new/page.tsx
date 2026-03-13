"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { customersApi } from "@/lib/api";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";

export default function NewCustomerPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    customer_type: "individual",
    name: "",
    phone: "",
    email: "",
    region: "",
    source_channel: "",
    grade: "normal",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await customersApi.create(form);
      router.push("/arki/customers");
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
      <h2 className="text-lg font-bold text-slate-900">고객 등록</h2>

      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="grid grid-cols-2 gap-4">
          <Select
            label="고객유형"
            options={[
              { value: "individual", label: "개인" },
              { value: "company", label: "법인" },
            ]}
            value={form.customer_type}
            onChange={(e) => update("customer_type", e.target.value)}
          />
          <Select
            label="등급"
            options={[
              { value: "normal", label: "일반" },
              { value: "repeat", label: "단골" },
              { value: "vip", label: "VIP" },
            ]}
            value={form.grade}
            onChange={(e) => update("grade", e.target.value)}
          />
        </div>

        <Input
          label="고객명 / 회사명"
          value={form.name}
          onChange={(e) => update("name", e.target.value)}
          required
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="연락처"
            type="tel"
            value={form.phone}
            onChange={(e) => update("phone", e.target.value)}
            placeholder="010-0000-0000"
          />
          <Input
            label="이메일"
            type="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="지역"
            value={form.region}
            onChange={(e) => update("region", e.target.value)}
            placeholder="서울, 경기 등"
          />
          <Select
            label="유입채널"
            options={[
              { value: "website", label: "웹사이트" },
              { value: "phone", label: "전화" },
              { value: "referral", label: "소개" },
              { value: "store", label: "매장방문" },
              { value: "other", label: "기타" },
            ]}
            placeholder="선택"
            value={form.source_channel}
            onChange={(e) => update("source_channel", e.target.value)}
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
