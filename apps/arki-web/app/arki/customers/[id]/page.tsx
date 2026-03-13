"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Edit2, Check, X } from "lucide-react";
import { customersApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface Customer {
  id: string;
  customer_type: string;
  name: string;
  phone: string | null;
  phone_masked: string | null;
  email: string | null;
  email_masked: string | null;
  region: string | null;
  address: string | null;
  source_channel: string | null;
  grade: string;
  is_vip: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const gradeLabels: Record<string, string> = {
  normal: "일반",
  repeat: "단골",
  vip: "VIP",
};

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingGrade, setEditingGrade] = useState(false);
  const [newGrade, setNewGrade] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    customersApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setCustomer(data);
        setNewGrade(data?.grade ?? "normal");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleGradeUpdate() {
    if (!customer) return;
    setSaving(true);
    try {
      await customersApi.update(id, { grade: newGrade });
      setCustomer((prev) => prev ? { ...prev, grade: newGrade, is_vip: newGrade === "vip" } : prev);
      setEditingGrade(false);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="고객 정보 로딩 중..." />;
  if (!customer) {
    return (
      <div className="py-16 text-center text-slate-400">
        고객 정보를 찾을 수 없습니다.
      </div>
    );
  }

  const infoFields = [
    { label: "고객 유형", value: customer.customer_type },
    { label: "고객명", value: customer.name },
    { label: "연락처", value: customer.phone_masked ?? customer.phone ?? "—" },
    { label: "이메일", value: customer.email_masked ?? customer.email ?? "—" },
    { label: "지역", value: customer.region ?? "—" },
    { label: "주소", value: customer.address ?? "—" },
    { label: "유입경로", value: customer.source_channel ?? "—" },
    { label: "메모", value: customer.notes ?? "—" },
    { label: "등록일", value: dayjs(customer.created_at).format("YYYY-MM-DD HH:mm") },
    { label: "수정일", value: dayjs(customer.updated_at).format("YYYY-MM-DD HH:mm") },
  ];

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/customers")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        고객 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">{customer.name}</h2>
        <Badge status={customer.grade}>{gradeLabels[customer.grade] ?? customer.grade}</Badge>
        {customer.is_vip && <Badge variant="purple">VIP</Badge>}
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">기본 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {infoFields.map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">
                {f.label}
              </dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">등급 관리</h3>
        {editingGrade ? (
          <div className="flex items-center gap-3">
            <Select
              options={[
                { value: "normal", label: "일반" },
                { value: "repeat", label: "단골" },
                { value: "vip", label: "VIP" },
              ]}
              value={newGrade}
              onChange={(e) => setNewGrade(e.target.value)}
              className="w-40"
            />
            <Button size="sm" onClick={handleGradeUpdate} loading={saving}>
              <Check className="h-4 w-4" />
              저장
            </Button>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setEditingGrade(false);
                setNewGrade(customer.grade);
              }}
            >
              <X className="h-4 w-4" />
              취소
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Badge status={customer.grade}>{gradeLabels[customer.grade] ?? customer.grade}</Badge>
            <Button size="sm" variant="secondary" onClick={() => setEditingGrade(true)}>
              <Edit2 className="h-4 w-4" />
              등급 변경
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
