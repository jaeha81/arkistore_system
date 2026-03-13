"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { purchaseRequestsApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface PurchaseRequestItem {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit: string;
  unit_price: number | null;
  notes: string | null;
}

interface PurchaseRequest {
  id: string;
  pr_number: string;
  request_date: string;
  requester: string;
  pr_status: string;
  notes: string | null;
  items: PurchaseRequestItem[];
  created_at: string;
  updated_at: string;
}

const statusLabels: Record<string, string> = {
  requested: "요청",
  reviewed: "검토",
  approved: "승인",
  rejected: "반려",
  converted_to_order: "발주전환",
};

export default function PurchaseRequestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [item, setItem] = useState<PurchaseRequest | null>(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    purchaseRequestsApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setItem(data);
        setNewStatus(data?.pr_status ?? "requested");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!item) return;
    setSaving(true);
    try {
      await purchaseRequestsApi.update(id, { pr_status: newStatus });
      setItem((prev) => prev ? { ...prev, pr_status: newStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="발주 요청 로딩 중..." />;
  if (!item) {
    return (
      <div className="py-16 text-center text-slate-400">
        발주 요청 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/purchase-requests")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        발주 요청 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">{item.pr_number}</h2>
        <Badge status={item.pr_status}>{statusLabels[item.pr_status] ?? item.pr_status}</Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">요청 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "요청번호", value: item.pr_number },
            { label: "요청일", value: dayjs(item.request_date).format("YYYY-MM-DD") },
            { label: "요청자", value: item.requester },
            { label: "비고", value: item.notes ?? "—" },
            { label: "등록일", value: dayjs(item.created_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">{f.label}</dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      {item.items && item.items.length > 0 && (
        <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h3 className="mb-4 font-semibold text-slate-900">품목 목록</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  {["상품명", "수량", "단위", "단가", "비고"].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {item.items.map((it) => (
                  <tr key={it.id}>
                    <td className="px-4 py-2 text-sm text-slate-900">{it.product_name}</td>
                    <td className="px-4 py-2 text-sm text-slate-700">{it.quantity}</td>
                    <td className="px-4 py-2 text-sm text-slate-700">{it.unit}</td>
                    <td className="px-4 py-2 text-sm text-slate-700">
                      {it.unit_price ? `${Number(it.unit_price).toLocaleString()}` : "—"}
                    </td>
                    <td className="px-4 py-2 text-sm text-slate-500">{it.notes ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">상태 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "requested", label: "요청" },
              { value: "reviewed", label: "검토" },
              { value: "approved", label: "승인" },
              { value: "rejected", label: "반려" },
              { value: "converted_to_order", label: "발주전환" },
            ]}
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={handleStatusUpdate}
            loading={saving}
            disabled={newStatus === item.pr_status}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
