"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { leadsApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface Lead {
  id: string;
  lead_number: string;
  company_name: string;
  contact_name: string;
  phone: string | null;
  email: string | null;
  lead_source: string;
  product_interest: string | null;
  budget: number | null;
  lead_status: string;
  assigned_to: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const statusLabels: Record<string, string> = {
  new: "신규",
  in_progress: "진행중",
  converted: "전환",
  closed: "종료",
  dropped: "이탈",
};

export default function LeadDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    leadsApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setLead(data);
        setNewStatus(data?.lead_status ?? "new");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!lead) return;
    setSaving(true);
    try {
      await leadsApi.update(id, { lead_status: newStatus });
      setLead((prev) => prev ? { ...prev, lead_status: newStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="리드 정보 로딩 중..." />;
  if (!lead) {
    return (
      <div className="py-16 text-center text-slate-400">
        리드 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/leads")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        리드 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">
          {lead.company_name} — {lead.contact_name}
        </h2>
        <Badge status={lead.lead_status}>{statusLabels[lead.lead_status] ?? lead.lead_status}</Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">리드 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "리드번호", value: lead.lead_number },
            { label: "회사명", value: lead.company_name },
            { label: "담당자", value: lead.contact_name },
            { label: "연락처", value: lead.phone ?? "—" },
            { label: "이메일", value: lead.email ?? "—" },
            { label: "유입경로", value: lead.lead_source },
            { label: "관심상품", value: lead.product_interest ?? "—" },
            { label: "예산", value: lead.budget ? `${Number(lead.budget).toLocaleString()}원` : "—" },
            { label: "담당자", value: lead.assigned_to ?? "—" },
            { label: "메모", value: lead.notes ?? "—" },
            { label: "등록일", value: dayjs(lead.created_at).format("YYYY-MM-DD HH:mm") },
            { label: "수정일", value: dayjs(lead.updated_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
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
        <h3 className="mb-4 font-semibold text-slate-900">상태 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "new", label: "신규" },
              { value: "in_progress", label: "진행중" },
              { value: "converted", label: "전환" },
              { value: "closed", label: "종료" },
              { value: "dropped", label: "이탈" },
            ]}
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={handleStatusUpdate}
            loading={saving}
            disabled={newStatus === lead.lead_status}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
