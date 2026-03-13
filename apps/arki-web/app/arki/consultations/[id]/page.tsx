"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { consultationsApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface Consultation {
  id: string;
  consultation_number: string;
  customer_id: string;
  customer_name: string;
  channel: string;
  sales_rep: string;
  consultation_date: string;
  scheduled_at: string | null;
  product_name: string;
  consultation_content: string | null;
  outcome: string | null;
  consultation_status: string;
  created_at: string;
  updated_at: string;
}

const statusLabels: Record<string, string> = {
  scheduled: "예약",
  in_progress: "진행중",
  completed: "완료",
  cancelled: "취소",
};

export default function ConsultationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [item, setItem] = useState<Consultation | null>(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    consultationsApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setItem(data);
        setNewStatus(data?.consultation_status ?? "scheduled");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!item) return;
    setSaving(true);
    try {
      await consultationsApi.update(id, { consultation_status: newStatus });
      setItem((prev) => prev ? { ...prev, consultation_status: newStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="상담 정보 로딩 중..." />;
  if (!item) {
    return (
      <div className="py-16 text-center text-slate-400">
        상담 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/consultations")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        상담 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">{item.consultation_number}</h2>
        <Badge status={item.consultation_status}>
          {statusLabels[item.consultation_status] ?? item.consultation_status}
        </Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">상담 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "상담번호", value: item.consultation_number },
            { label: "고객명", value: item.customer_name },
            { label: "채널", value: item.channel },
            { label: "담당자", value: item.sales_rep },
            { label: "상담일", value: dayjs(item.consultation_date).format("YYYY-MM-DD") },
            { label: "예약 시각", value: item.scheduled_at ? dayjs(item.scheduled_at).format("YYYY-MM-DD HH:mm") : "—" },
            { label: "관심상품", value: item.product_name },
            { label: "등록일", value: dayjs(item.created_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">
                {f.label}
              </dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
        </dl>

        {item.consultation_content && (
          <div className="mt-4">
            <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">상담 내용</dt>
            <dd className="mt-1 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 whitespace-pre-wrap">
              {item.consultation_content}
            </dd>
          </div>
        )}

        {item.outcome && (
          <div className="mt-4">
            <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">결과</dt>
            <dd className="mt-1 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 whitespace-pre-wrap">
              {item.outcome}
            </dd>
          </div>
        )}
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">상태 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "scheduled", label: "예약" },
              { value: "in_progress", label: "진행중" },
              { value: "completed", label: "완료" },
              { value: "cancelled", label: "취소" },
            ]}
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={handleStatusUpdate}
            loading={saving}
            disabled={newStatus === item.consultation_status}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
