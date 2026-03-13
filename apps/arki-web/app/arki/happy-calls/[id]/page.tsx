"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { happyCallsApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface HappyCall {
  id: string;
  delivery_id: string;
  call_date: string;
  caller_name: string;
  call_result: string;
  satisfaction_score: number | null;
  callback_required: boolean;
  notes: string | null;
  created_at: string;
}

const resultLabels: Record<string, string> = {
  satisfied: "만족",
  neutral: "보통",
  unsatisfied: "불만족",
  no_answer: "부재",
};

const resultBadgeStatus: Record<string, string> = {
  satisfied: "completed",
  neutral: "pending",
  unsatisfied: "cancelled",
  no_answer: "inactive",
};

export default function HappyCallDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [item, setItem] = useState<HappyCall | null>(null);
  const [loading, setLoading] = useState(true);
  const [newResult, setNewResult] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    happyCallsApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setItem(data);
        setNewResult(data?.call_result ?? "no_answer");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleResultUpdate() {
    if (!item) return;
    setSaving(true);
    try {
      await happyCallsApi.update(id, { call_result: newResult });
      setItem((prev) => prev ? { ...prev, call_result: newResult } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="해피콜 정보 로딩 중..." />;
  if (!item) {
    return (
      <div className="py-16 text-center text-slate-400">
        해피콜 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/happy-calls")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        해피콜 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">해피콜 상세</h2>
        <Badge status={resultBadgeStatus[item.call_result] ?? "gray"}>
          {resultLabels[item.call_result] ?? item.call_result}
        </Badge>
        {item.callback_required && <Badge variant="yellow">콜백 필요</Badge>}
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">통화 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "배송 ID", value: item.delivery_id.slice(0, 8) + "..." },
            { label: "통화일", value: dayjs(item.call_date).format("YYYY-MM-DD") },
            { label: "담당자", value: item.caller_name },
            { label: "만족도 점수", value: item.satisfaction_score != null ? `${item.satisfaction_score}점` : "—" },
            { label: "콜백 필요", value: item.callback_required ? "필요" : "불필요" },
            { label: "등록일", value: dayjs(item.created_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">{f.label}</dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
          {item.notes && (
            <div className="col-span-2">
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">메모</dt>
              <dd className="mt-1 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 whitespace-pre-wrap">
                {item.notes}
              </dd>
            </div>
          )}
        </dl>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">결과 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "satisfied", label: "만족" },
              { value: "neutral", label: "보통" },
              { value: "unsatisfied", label: "불만족" },
              { value: "no_answer", label: "부재" },
            ]}
            value={newResult}
            onChange={(e) => setNewResult(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={handleResultUpdate}
            loading={saving}
            disabled={newResult === item.call_result}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
