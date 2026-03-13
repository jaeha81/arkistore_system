"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { purchaseOrdersApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface PurchaseOrder {
  id: string;
  po_number: string;
  pr_id: string | null;
  supplier: string;
  order_date: string;
  expected_delivery_date: string | null;
  po_status: string;
  total_amount: number;
  currency: string;
  payment_terms: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const statusLabels: Record<string, string> = {
  created: "생성",
  ordered: "발주",
  invoiced: "인보이스",
  shipped: "선적",
  completed: "완료",
  cancelled: "취소",
};

export default function PurchaseOrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [po, setPo] = useState<PurchaseOrder | null>(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    purchaseOrdersApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setPo(data);
        setNewStatus(data?.po_status ?? "created");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!po) return;
    setSaving(true);
    try {
      await purchaseOrdersApi.update(id, { po_status: newStatus });
      setPo((prev) => prev ? { ...prev, po_status: newStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="발주서 로딩 중..." />;
  if (!po) {
    return (
      <div className="py-16 text-center text-slate-400">
        발주서를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/purchase-orders")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        발주서 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">{po.po_number}</h2>
        <Badge status={po.po_status}>{statusLabels[po.po_status] ?? po.po_status}</Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">발주서 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "발주번호", value: po.po_number },
            { label: "공급업체", value: po.supplier },
            { label: "발주일", value: dayjs(po.order_date).format("YYYY-MM-DD") },
            { label: "입고예정일", value: po.expected_delivery_date ? dayjs(po.expected_delivery_date).format("YYYY-MM-DD") : "—" },
            { label: "금액", value: `${Number(po.total_amount).toLocaleString()} ${po.currency}` },
            { label: "결제 조건", value: po.payment_terms ?? "—" },
            { label: "비고", value: po.notes ?? "—" },
            { label: "등록일", value: dayjs(po.created_at).format("YYYY-MM-DD HH:mm") },
            { label: "수정일", value: dayjs(po.updated_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">{f.label}</dt>
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
              { value: "created", label: "생성" },
              { value: "ordered", label: "발주" },
              { value: "invoiced", label: "인보이스" },
              { value: "shipped", label: "선적" },
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
            disabled={newStatus === po.po_status}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
