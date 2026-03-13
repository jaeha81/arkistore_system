"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { deliveriesApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface Delivery {
  id: string;
  delivery_number: string | null;
  contract_id: string;
  customer_id: string;
  delivery_date: string;
  time_slot: string;
  delivery_team: string;
  vehicle_code: string | null;
  address_text: string;
  floor: number | null;
  ladder_required: boolean;
  delivery_status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const statusLabels: Record<string, string> = {
  scheduled: "예약",
  confirmed: "확정",
  in_transit: "배송중",
  completed: "완료",
  delayed: "지연",
  cancelled: "취소",
};

export default function DeliveryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [delivery, setDelivery] = useState<Delivery | null>(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    deliveriesApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setDelivery(data);
        setNewStatus(data?.delivery_status ?? "scheduled");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!delivery) return;
    setSaving(true);
    try {
      await deliveriesApi.update(id, { delivery_status: newStatus });
      setDelivery((prev) => prev ? { ...prev, delivery_status: newStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="배송 정보 로딩 중..." />;
  if (!delivery) {
    return (
      <div className="py-16 text-center text-slate-400">
        배송 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/deliveries")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        배송 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">
          {delivery.delivery_number ?? "배송번호 미지정"}
        </h2>
        <Badge status={delivery.delivery_status}>
          {statusLabels[delivery.delivery_status] ?? delivery.delivery_status}
        </Badge>
        {delivery.ladder_required && <Badge variant="yellow">사다리차 필요</Badge>}
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">배송 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "배송번호", value: delivery.delivery_number ?? "—" },
            { label: "배송일", value: dayjs(delivery.delivery_date).format("YYYY-MM-DD") },
            { label: "시간대", value: delivery.time_slot },
            { label: "배송팀", value: delivery.delivery_team },
            { label: "차량코드", value: delivery.vehicle_code ?? "—" },
            { label: "층수", value: delivery.floor ? `${delivery.floor}층` : "—" },
            { label: "사다리차", value: delivery.ladder_required ? "필요" : "불필요" },
            { label: "비고", value: delivery.notes ?? "—" },
            { label: "등록일", value: dayjs(delivery.created_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">{f.label}</dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
          <div className="col-span-2">
            <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">배송지</dt>
            <dd className="mt-1 text-sm text-slate-900">{delivery.address_text}</dd>
          </div>
        </dl>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">배송 상태 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "scheduled", label: "예약" },
              { value: "confirmed", label: "확정" },
              { value: "in_transit", label: "배송중" },
              { value: "completed", label: "완료" },
              { value: "delayed", label: "지연" },
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
            disabled={newStatus === delivery.delivery_status}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
